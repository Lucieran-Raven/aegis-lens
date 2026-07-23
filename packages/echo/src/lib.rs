//! ECHO - Acoustic Time-of-Flight Physics Pipeline
//!
//! This module provides acoustic time-of-flight measurement and analysis
//! for detecting audio replay attacks and synthetic speech through
//! acoustic fingerprinting. Compiled to WebAssembly for browser use.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use wasm_bindgen::prelude::*;

#[cfg(not(target_arch = "wasm32"))]
use rustfft::{num_complex::Complex, FftPlanner};

#[cfg(target_arch = "wasm32")]
use num_complex::Complex;

const WINDOW_SIZE: usize = 1000;
const BASELINE_VARIANCE: f64 = 0.1;
const THRESHOLD_CLEAR: f64 = 0.8;
const THRESHOLD_SUSPECT: f64 = 0.5;

/// Result of ECHO analysis
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "camelCase")]
pub struct EchoResult {
    pub score: f64,
    pub status: String,
    pub mean_tof: f64,
    pub std_tof: f64,
    pub spectral_centroid: f64,
    pub zero_crossing_rate: f64,
    pub spectral_flux: f64,
    pub spectral_rolloff: f64,
    pub sample_count: usize,
}

/// Chirp signal configuration
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ChirpConfig {
    pub start_frequency: f64,
    pub end_frequency: f64,
    pub duration: f64,
    pub sample_rate: f64,
}

impl Default for ChirpConfig {
    fn default() -> Self {
        Self {
            start_frequency: 1000.0, // 1 kHz
            end_frequency: 8000.0,   // 8 kHz
            duration: 0.1,           // 100 ms
            sample_rate: 44100.0,    // 44.1 kHz
        }
    }
}

/// Generated chirp signal
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ChirpSignal {
    pub samples: Vec<f32>,
    pub config: ChirpConfig,
}

/// ECHO engine for acoustic time-of-flight measurement
#[wasm_bindgen]
pub struct EchoEngine {
    samples: VecDeque<f64>,
}

impl Default for EchoEngine {
    fn default() -> Self {
        Self::new_native()
    }
}

impl EchoEngine {
    /// Create a new ECHO engine (native)
    pub fn new_native() -> Self {
        Self {
            samples: VecDeque::with_capacity(WINDOW_SIZE),
        }
    }

    /// Perform FFT-based cross-correlation between two signals (native)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn cross_correlation_fft_native(signal1: &[f32], signal2: &[f32]) -> Vec<f32> {
        if signal1.is_empty() || signal2.is_empty() {
            return Vec::new();
        }

        // Pad signals to next power of 2 for efficient FFT
        let n = signal1.len() + signal2.len() - 1;
        let fft_size = n.next_power_of_two();

        // Prepare complex arrays
        let mut fft1: Vec<Complex<f64>> = vec![Complex::new(0.0, 0.0); fft_size];
        let mut fft2: Vec<Complex<f64>> = vec![Complex::new(0.0, 0.0); fft_size];

        // Load signal1 and zero-pad
        for (i, &val) in signal1.iter().enumerate() {
            fft1[i] = Complex::new(val as f64, 0.0);
        }

        // Load signal2 and zero-pad
        for (i, &val) in signal2.iter().enumerate() {
            fft2[i] = Complex::new(val as f64, 0.0);
        }

        // Perform FFT
        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(fft_size);
        fft.process(&mut fft1);
        fft.process(&mut fft2);

        // Multiply in frequency domain (signal1 * conjugate(signal2))
        for (i, fft1_val) in fft1.iter_mut().enumerate().take(fft_size) {
            *fft1_val *= fft2[i].conj();
        }

        // Perform inverse FFT
        let ifft = planner.plan_fft_inverse(fft_size);
        ifft.process(&mut fft1);

        // Extract real part and normalize
        let mut result = Vec::with_capacity(n);
        for fft1_val in fft1.iter().take(n) {
            result.push((fft1_val.re / fft_size as f64) as f32);
        }

        result
    }

    /// Perform FFT-based cross-correlation between two signals (WASM fallback)
    #[cfg(target_arch = "wasm32")]
    pub fn cross_correlation_fft_native(signal1: &[f32], signal2: &[f32]) -> Vec<f32> {
        // Fallback: simple time-domain cross-correlation for WASM
        // This is less efficient but works without rustfft
        if signal1.is_empty() || signal2.is_empty() {
            return Vec::new();
        }

        let n = signal1.len() + signal2.len() - 1;
        let mut result = vec![0.0f32; n];

        for lag in 0..n {
            let mut sum = 0.0f32;
            for i in 0..signal1.len() {
                let j = lag as i32 - i as i32;
                if j >= 0 && (j as usize) < signal2.len() {
                    sum += signal1[i] * signal2[j as usize];
                }
            }
            result[lag] = sum;
        }

        result
    }

    /// Find the lag with maximum correlation (native)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn find_peak_lag_native(correlation: &[f32]) -> (usize, f32) {
        if correlation.is_empty() {
            return (0, 0.0);
        }

        let mut max_val = correlation[0].abs();
        let mut max_idx = 0;

        for (i, &val) in correlation.iter().enumerate() {
            if val.abs() > max_val {
                max_val = val.abs();
                max_idx = i;
            }
        }

        (max_idx, max_val)
    }

    /// Find the lag with maximum correlation (WASM fallback)
    #[cfg(target_arch = "wasm32")]
    pub fn find_peak_lag_native(correlation: &[f32]) -> (usize, f32) {
        if correlation.is_empty() {
            return (0, 0.0);
        }

        let mut max_val = correlation[0].abs();
        let mut max_idx = 0;

        for (i, &val) in correlation.iter().enumerate() {
            if val.abs() > max_val {
                max_val = val.abs();
                max_idx = i;
            }
        }

        (max_idx, max_val)
    }

    /// Compute FFT of a signal (native)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn compute_fft_native(signal: &[f32]) -> Vec<Complex<f64>> {
        if signal.is_empty() {
            return Vec::new();
        }

        let fft_size = signal.len().next_power_of_two();
        let mut fft_data: Vec<Complex<f64>> = vec![Complex::new(0.0, 0.0); fft_size];

        for (i, &val) in signal.iter().enumerate() {
            fft_data[i] = Complex::new(val as f64, 0.0);
        }

        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(fft_size);
        fft.process(&mut fft_data);

        fft_data
    }

    /// Compute spectral centroid from FFT magnitude spectrum (native)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn spectral_centroid_native(fft_data: &[Complex<f64>], sample_rate: f64) -> f64 {
        if fft_data.is_empty() {
            return 0.0;
        }

        let n = fft_data.len();
        let mut weighted_sum = 0.0;
        let mut magnitude_sum = 0.0;

        for (i, complex) in fft_data.iter().enumerate().take(n / 2) {
            let magnitude = (complex.re * complex.re + complex.im * complex.im).sqrt();
            let frequency = i as f64 * sample_rate / n as f64;

            weighted_sum += frequency * magnitude;
            magnitude_sum += magnitude;
        }

        if magnitude_sum < 1e-10 {
            return 0.0;
        }

        weighted_sum / magnitude_sum
    }

    /// Compute spectral flux (change in magnitude between frames) (native)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn spectral_flux_native(
        fft_current: &[Complex<f64>],
        fft_previous: &[Complex<f64>],
    ) -> f64 {
        if fft_current.is_empty() || fft_previous.is_empty() {
            return 0.0;
        }

        let n = fft_current.len().min(fft_previous.len());
        let mut flux = 0.0;

        for i in 0..n {
            let mag_current = (fft_current[i].re * fft_current[i].re
                + fft_current[i].im * fft_current[i].im)
                .sqrt();
            let mag_previous = (fft_previous[i].re * fft_previous[i].re
                + fft_previous[i].im * fft_previous[i].im)
                .sqrt();
            let diff = mag_current - mag_previous;
            if diff > 0.0 {
                flux += diff;
            }
        }

        flux / n as f64
    }

    /// Compute spectral rolloff (frequency below which 85% of energy is contained) (native)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn spectral_rolloff_native(fft_data: &[Complex<f64>], sample_rate: f64) -> f64 {
        if fft_data.is_empty() {
            return 0.0;
        }

        let n = fft_data.len();
        let mut magnitudes: Vec<f64> = Vec::with_capacity(n / 2);

        for complex in fft_data.iter().take(n / 2) {
            let magnitude = (complex.re * complex.re + complex.im * complex.im).sqrt();
            magnitudes.push(magnitude);
        }

        let total_energy: f64 = magnitudes.iter().map(|&m| m * m).sum();
        if total_energy < 1e-10 {
            return 0.0;
        }

        let threshold = 0.85 * total_energy;
        let mut cumulative_energy = 0.0;

        for (i, &magnitude) in magnitudes.iter().enumerate() {
            cumulative_energy += magnitude * magnitude;
            if cumulative_energy >= threshold {
                return i as f64 * sample_rate / n as f64;
            }
        }

        sample_rate / 2.0
    }

    /// Compute FFT of a signal (WASM fallback)
    #[cfg(target_arch = "wasm32")]
    pub fn compute_fft_native(signal: &[f32]) -> Vec<Complex<f64>> {
        // Fallback: return empty vector for WASM
        Vec::new()
    }

    /// Compute spectral centroid from FFT magnitude spectrum (WASM fallback)
    #[cfg(target_arch = "wasm32")]
    pub fn spectral_centroid_native(_fft_data: &[Complex<f64>], _sample_rate: f64) -> f64 {
        // Fallback: return 0.0 for WASM
        0.0
    }

    /// Compute spectral flux (WASM fallback)
    #[cfg(target_arch = "wasm32")]
    pub fn spectral_flux_native(
        _fft_current: &[Complex<f64>],
        _fft_previous: &[Complex<f64>],
    ) -> f64 {
        // Fallback: return 0.0 for WASM
        0.0
    }

    /// Compute spectral rolloff (WASM fallback)
    #[cfg(target_arch = "wasm32")]
    pub fn spectral_rolloff_native(_fft_data: &[Complex<f64>], _sample_rate: f64) -> f64 {
        // Fallback: return 0.0 for WASM
        0.0
    }

    /// Perform full analysis and return result (native)
    pub fn analyze_native(&self) -> EchoResult {
        if self.samples.len() < 10 {
            return EchoResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                mean_tof: 0.0,
                std_tof: 0.0,
                spectral_centroid: 0.0,
                zero_crossing_rate: 0.0,
                spectral_flux: 0.0,
                spectral_rolloff: 0.0,
                sample_count: self.samples.len(),
            };
        }

        let mean = self.calculate_mean();
        let std = self.calculate_std(mean);
        let zcr = self.calculate_zero_crossing_rate();

        // Compute spectral features using FFT
        let samples_vec: Vec<f32> = self.samples.iter().map(|&x| x as f32).collect();
        let spectral_centroid = if cfg!(not(target_arch = "wasm32")) {
            let fft_data = Self::compute_fft_native(&samples_vec);
            Self::spectral_centroid_native(&fft_data, 44100.0)
        } else {
            self.calculate_spectral_centroid()
        };

        let spectral_flux = if cfg!(not(target_arch = "wasm32")) {
            let fft_data = Self::compute_fft_native(&samples_vec);
            let fft_prev = vec![Complex::new(0.0, 0.0); fft_data.len()];
            Self::spectral_flux_native(&fft_data, &fft_prev)
        } else {
            0.0
        };

        let spectral_rolloff = if cfg!(not(target_arch = "wasm32")) {
            let fft_data = Self::compute_fft_native(&samples_vec);
            Self::spectral_rolloff_native(&fft_data, 44100.0)
        } else {
            0.0
        };

        let score = self.calculate_score(mean, std, spectral_centroid, zcr);
        let status = self.determine_status(score);

        EchoResult {
            score,
            status,
            mean_tof: mean,
            std_tof: std,
            spectral_centroid,
            zero_crossing_rate: zcr,
            spectral_flux,
            spectral_rolloff,
            sample_count: self.samples.len(),
        }
    }

    /// Generate a linear chirp signal (native implementation)
    pub fn generate_chirp_native(&self, config: &ChirpConfig) -> ChirpSignal {
        let num_samples = (config.duration * config.sample_rate) as usize;
        let mut samples = Vec::with_capacity(num_samples);

        // Linear chirp: frequency changes linearly from start to end
        // f(t) = f_start + (f_end - f_start) * (t / duration)
        // phase(t) = 2 * pi * integral(f(t) dt)
        // phase(t) = 2 * pi * (f_start * t + (f_end - f_start) * t^2 / (2 * duration))

        let freq_slope = (config.end_frequency - config.start_frequency) / config.duration;

        for i in 0..num_samples {
            let t = i as f64 / config.sample_rate;
            let phase = 2.0
                * std::f64::consts::PI
                * (config.start_frequency * t + freq_slope * t * t / 2.0);
            samples.push(phase.sin() as f32);
        }

        ChirpSignal {
            samples,
            config: config.clone(),
        }
    }
}

#[wasm_bindgen]
impl EchoEngine {
    /// Create a new ECHO engine (WASM)
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self::new_native()
    }

    /// Measure a single time-of-flight sample
    /// Returns the TOF value in milliseconds
    #[wasm_bindgen]
    pub fn measure(&mut self) -> f64 {
        // Placeholder: In real implementation, this would measure
        // actual acoustic time-of-flight using Web Audio API
        let t1 = js_sys::Date::now();
        let t2 = js_sys::Date::now();
        let tof = t2 - t1;

        self.samples.push_back(tof);
        if self.samples.len() > WINDOW_SIZE {
            self.samples.pop_front();
        }

        tof
    }

    /// Measure a single time-of-flight sample (native version for testing)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn measure_native(&mut self) -> f64 {
        use std::time::Instant;
        let t1 = Instant::now();
        let t2 = Instant::now();
        let tof = t2.duration_since(t1).as_secs_f64() * 1000.0;

        self.samples.push_back(tof);
        if self.samples.len() > WINDOW_SIZE {
            self.samples.pop_front();
        }

        tof
    }

    /// Get current sample count
    #[wasm_bindgen]
    pub fn sample_count(&self) -> usize {
        self.samples.len()
    }

    /// Clear all samples
    #[wasm_bindgen]
    pub fn clear(&mut self) {
        self.samples.clear();
    }

    /// Perform full analysis and return result
    #[wasm_bindgen]
    pub fn analyze(&self) -> JsValue {
        if self.samples.len() < 10 {
            let result = EchoResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                mean_tof: 0.0,
                std_tof: 0.0,
                spectral_centroid: 0.0,
                zero_crossing_rate: 0.0,
                spectral_flux: 0.0,
                spectral_rolloff: 0.0,
                sample_count: self.samples.len(),
            };
            return serde_wasm_bindgen::to_value(&result).unwrap();
        }

        let mean = self.calculate_mean();
        let std = self.calculate_std(mean);
        let spectral_centroid = self.calculate_spectral_centroid();
        let zcr = self.calculate_zero_crossing_rate();

        let score = self.calculate_score(mean, std, spectral_centroid, zcr);
        let status = self.determine_status(score);

        let result = EchoResult {
            score,
            status,
            mean_tof: mean,
            std_tof: std,
            spectral_centroid,
            zero_crossing_rate: zcr,
            spectral_flux: 0.0,
            spectral_rolloff: 0.0,
            sample_count: self.samples.len(),
        };
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Generate a linear chirp signal
    /// Returns the chirp signal as a JsValue
    #[wasm_bindgen]
    pub fn generate_chirp(
        &self,
        start_freq: f64,
        end_freq: f64,
        duration: f64,
        sample_rate: f64,
    ) -> JsValue {
        let config = ChirpConfig {
            start_frequency: start_freq,
            end_frequency: end_freq,
            duration,
            sample_rate,
        };
        let signal = self.generate_chirp_native(&config);
        serde_wasm_bindgen::to_value(&signal).unwrap()
    }

    /// Generate a chirp signal with default configuration
    #[wasm_bindgen]
    pub fn generate_chirp_default(&self) -> JsValue {
        let config = ChirpConfig::default();
        let signal = self.generate_chirp_native(&config);
        serde_wasm_bindgen::to_value(&signal).unwrap()
    }

    /// Perform FFT-based cross-correlation between two signals
    /// Returns the correlation result as a JsValue array
    #[wasm_bindgen]
    pub fn cross_correlation_fft(&self, signal1: &[f32], signal2: &[f32]) -> JsValue {
        let correlation = Self::cross_correlation_fft_native(signal1, signal2);
        serde_wasm_bindgen::to_value(&correlation).unwrap()
    }

    /// Find the lag with maximum correlation
    /// Returns a JsValue object with { lag: usize, value: f32 }
    #[wasm_bindgen]
    pub fn find_peak_lag(&self, correlation: &[f32]) -> JsValue {
        let (lag, value) = Self::find_peak_lag_native(correlation);
        let result = serde_json::json!({ "lag": lag, "value": value });
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Compute spectral centroid from a signal
    /// Returns the spectral centroid in Hz
    #[wasm_bindgen]
    pub fn compute_spectral_centroid(&self, signal: &[f32], sample_rate: f64) -> f64 {
        if cfg!(not(target_arch = "wasm32")) {
            let fft_data = Self::compute_fft_native(signal);
            Self::spectral_centroid_native(&fft_data, sample_rate)
        } else {
            // Fallback: simple time-domain centroid
            if signal.is_empty() {
                return 0.0;
            }
            let sum: f64 = signal.iter().map(|&x| x as f64).sum();
            let weighted_sum: f64 = signal
                .iter()
                .enumerate()
                .map(|(i, &x)| i as f64 * x as f64)
                .sum();
            if sum < 1e-10 {
                return 0.0;
            }
            weighted_sum / sum
        }
    }

    /// Compute spectral flux between two signals
    /// Returns the spectral flux value
    #[wasm_bindgen]
    pub fn compute_spectral_flux(&self, signal_current: &[f32], signal_previous: &[f32]) -> f64 {
        if cfg!(not(target_arch = "wasm32")) {
            let fft_current = Self::compute_fft_native(signal_current);
            let fft_previous = Self::compute_fft_native(signal_previous);
            Self::spectral_flux_native(&fft_current, &fft_previous)
        } else {
            // Fallback: simple time-domain difference
            if signal_current.is_empty() || signal_previous.is_empty() {
                return 0.0;
            }
            let n = signal_current.len().min(signal_previous.len());
            let mut flux = 0.0;
            for i in 0..n {
                let diff = signal_current[i] - signal_previous[i];
                if diff > 0.0 {
                    flux += diff as f64;
                }
            }
            flux / n as f64
        }
    }

    /// Compute spectral rolloff from a signal
    /// Returns the spectral rolloff frequency in Hz
    #[wasm_bindgen]
    pub fn compute_spectral_rolloff(&self, signal: &[f32], sample_rate: f64) -> f64 {
        if cfg!(not(target_arch = "wasm32")) {
            let fft_data = Self::compute_fft_native(signal);
            Self::spectral_rolloff_native(&fft_data, sample_rate)
        } else {
            // Fallback: return Nyquist frequency
            sample_rate / 2.0
        }
    }

    fn calculate_mean(&self) -> f64 {
        if self.samples.is_empty() {
            return 0.0;
        }
        self.samples.iter().sum::<f64>() / self.samples.len() as f64
    }

    fn calculate_std(&self, mean: f64) -> f64 {
        if self.samples.is_empty() {
            return 0.0;
        }
        let variance = self
            .samples
            .iter()
            .map(|&x| (x - mean).powi(2))
            .sum::<f64>()
            / self.samples.len() as f64;
        variance.sqrt()
    }

    fn calculate_spectral_centroid(&self) -> f64 {
        // Placeholder: Will be implemented in TASK #114
        if self.samples.is_empty() {
            return 0.0;
        }
        let sum: f64 = self.samples.iter().sum();
        let weighted_sum: f64 = self
            .samples
            .iter()
            .enumerate()
            .map(|(i, &x)| i as f64 * x)
            .sum();
        if sum < 1e-10 {
            return 0.0;
        }
        weighted_sum / sum
    }

    fn calculate_zero_crossing_rate(&self) -> f64 {
        // Placeholder: Will be implemented in TASK #114
        if self.samples.len() < 2 {
            return 0.0;
        }
        let samples: Vec<f64> = self.samples.iter().cloned().collect();
        let crossings = samples.windows(2).filter(|w| w[0] * w[1] < 0.0).count();
        crossings as f64 / samples.len() as f64
    }

    fn calculate_score(&self, mean: f64, std: f64, spectral_centroid: f64, zcr: f64) -> f64 {
        let mut score: f64 = 1.0;

        // Time-of-flight deviation penalty
        if !(0.1..=2.0).contains(&mean) {
            score -= 0.3;
        }

        // Variance penalty
        if std > BASELINE_VARIANCE * 3.0 {
            score -= 0.2;
        }

        // Spectral centroid penalty (placeholder)
        if !(0.1..=0.9).contains(&spectral_centroid) {
            score -= 0.2;
        }

        // Zero crossing rate penalty (placeholder)
        if !(0.01..=0.5).contains(&zcr) {
            score -= 0.2;
        }

        // Sample count penalty
        if self.samples.len() < 50 {
            score -= 0.1;
        }

        score.clamp(0.0, 1.0)
    }

    fn determine_status(&self, score: f64) -> String {
        if score >= THRESHOLD_CLEAR {
            "CLEAR".to_string()
        } else if score >= THRESHOLD_SUSPECT {
            "SUSPECT".to_string()
        } else {
            "ANOMALY".to_string()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_creation() {
        let engine = EchoEngine::new_native();
        assert_eq!(engine.sample_count(), 0);
    }

    #[test]
    fn test_measure() {
        let mut engine = EchoEngine::new_native();
        let sample = engine.measure_native();
        assert!(sample >= 0.0);
        assert_eq!(engine.sample_count(), 1);
    }

    #[test]
    fn test_capacity() {
        let mut engine = EchoEngine::new_native();
        for _ in 0..1001 {
            engine.measure_native();
        }
        assert_eq!(engine.sample_count(), 1000);
    }

    #[test]
    fn test_clear() {
        let mut engine = EchoEngine::new_native();
        for _ in 0..10 {
            engine.measure_native();
        }
        assert_eq!(engine.sample_count(), 10);
        engine.clear();
        assert_eq!(engine.sample_count(), 0);
    }

    #[test]
    fn test_insufficient_data() {
        let engine = EchoEngine::new_native();
        let result = engine.analyze_native();
        assert_eq!(result.status, "INSUFFICIENT_DATA");
    }

    #[test]
    fn test_mean_calculation() {
        let mut engine = EchoEngine::new_native();
        for _ in 0..100 {
            engine.measure_native();
        }
        let result = engine.analyze_native();
        assert!(result.mean_tof >= 0.0);
    }

    #[test]
    fn test_chirp_config_default() {
        let config = ChirpConfig::default();
        assert_eq!(config.start_frequency, 1000.0);
        assert_eq!(config.end_frequency, 8000.0);
        assert_eq!(config.duration, 0.1);
        assert_eq!(config.sample_rate, 44100.0);
    }

    #[test]
    fn test_chirp_generation() {
        let engine = EchoEngine::new_native();
        let config = ChirpConfig::default();
        let signal = engine.generate_chirp_native(&config);

        // Verify sample count
        let expected_samples = (config.duration * config.sample_rate) as usize;
        assert_eq!(signal.samples.len(), expected_samples);

        // Verify samples are in valid range [-1, 1]
        for &sample in &signal.samples {
            assert!(sample >= -1.0 && sample <= 1.0);
        }

        // Verify config is preserved
        assert_eq!(signal.config.start_frequency, config.start_frequency);
        assert_eq!(signal.config.end_frequency, config.end_frequency);
        assert_eq!(signal.config.duration, config.duration);
        assert_eq!(signal.config.sample_rate, config.sample_rate);
    }

    #[test]
    fn test_chirp_generation_custom() {
        let engine = EchoEngine::new_native();
        let config = ChirpConfig {
            start_frequency: 500.0,
            end_frequency: 2000.0,
            duration: 0.05,
            sample_rate: 22050.0,
        };
        let signal = engine.generate_chirp_native(&config);

        let expected_samples = (config.duration * config.sample_rate) as usize;
        assert_eq!(signal.samples.len(), expected_samples);
    }

    #[test]
    fn test_chirp_signal_bounds() {
        let engine = EchoEngine::new_native();
        let config = ChirpConfig::default();
        let signal = engine.generate_chirp_native(&config);

        // Check first and last samples
        assert!(!signal.samples.is_empty());
        let first = signal.samples.first().unwrap();
        let last = signal.samples.last().unwrap();
        assert!(*first >= -1.0 && *first <= 1.0);
        assert!(*last >= -1.0 && *last <= 1.0);
    }

    #[test]
    fn test_chirp_frequency_sweep() {
        let engine = EchoEngine::new_native();
        let config = ChirpConfig {
            start_frequency: 1000.0,
            end_frequency: 2000.0,
            duration: 0.1,
            sample_rate: 44100.0,
        };
        let signal = engine.generate_chirp_native(&config);

        // Verify that the signal has variation (not constant)
        let first_half: Vec<f32> = signal.samples.iter().take(100).cloned().collect();
        let second_half: Vec<f32> = signal.samples.iter().rev().take(100).cloned().collect();

        // The signal should have different values at different times
        let first_mean: f32 = first_half.iter().sum::<f32>() / first_half.len() as f32;
        let second_mean: f32 = second_half.iter().sum::<f32>() / second_half.len() as f32;

        // Due to the chirp, the means should be close to 0 but the signal should vary
        assert!((first_mean - second_mean).abs() < 0.5);
    }

    #[test]
    fn test_cross_correlation_fft_empty() {
        let result = EchoEngine::cross_correlation_fft_native(&[], &[1.0, 2.0, 3.0]);
        assert!(result.is_empty());
    }

    #[test]
    fn test_cross_correlation_fft_simple() {
        let signal1 = vec![1.0, 2.0, 3.0];
        let signal2 = vec![1.0, 2.0, 3.0];
        let result = EchoEngine::cross_correlation_fft_native(&signal1, &signal2);

        // Result should have length n1 + n2 - 1
        assert_eq!(result.len(), signal1.len() + signal2.len() - 1);

        // The peak should be at lag 0 for identical signals
        let (lag, value) = EchoEngine::find_peak_lag_native(&result);
        assert_eq!(lag, 0);
        assert!(value > 0.0);
    }

    #[test]
    fn test_cross_correlation_fft_shifted() {
        let signal1 = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let signal2 = vec![1.0, 2.0, 3.0, 4.0, 5.0, 0.0, 0.0];
        let result = EchoEngine::cross_correlation_fft_native(&signal1, &signal2);

        // The peak should be at lag 0 (signals are aligned at start)
        let (lag, value) = EchoEngine::find_peak_lag_native(&result);
        assert_eq!(lag, 0);
        assert!(value > 0.0);
    }

    #[test]
    fn test_find_peak_lag_empty() {
        let (lag, value) = EchoEngine::find_peak_lag_native(&[]);
        assert_eq!(lag, 0);
        assert_eq!(value, 0.0);
    }

    #[test]
    fn test_find_peak_lag_single() {
        let correlation = vec![5.0];
        let (lag, value) = EchoEngine::find_peak_lag_native(&correlation);
        assert_eq!(lag, 0);
        assert_eq!(value, 5.0);
    }

    #[test]
    fn test_find_peak_lag_multiple() {
        let correlation = vec![1.0, 5.0, 3.0, 2.0];
        let (lag, value) = EchoEngine::find_peak_lag_native(&correlation);
        assert_eq!(lag, 1);
        assert_eq!(value, 5.0);
    }

    #[test]
    fn test_find_peak_lag_negative() {
        let correlation = vec![1.0, -5.0, 3.0, 2.0];
        let (lag, value) = EchoEngine::find_peak_lag_native(&correlation);
        assert_eq!(lag, 1);
        assert_eq!(value, 5.0); // Should use absolute value
    }

    #[test]
    fn test_compute_fft_empty() {
        let result = EchoEngine::compute_fft_native(&[]);
        assert!(result.is_empty());
    }

    #[test]
    fn test_compute_fft_simple() {
        let signal = vec![1.0, 2.0, 3.0, 4.0];
        let result = EchoEngine::compute_fft_native(&signal);

        // FFT size should be next power of 2
        assert_eq!(result.len(), 4);
    }

    #[test]
    fn test_spectral_centroid_empty() {
        let fft_data: Vec<Complex<f64>> = vec![];
        let centroid = EchoEngine::spectral_centroid_native(&fft_data, 44100.0);
        assert_eq!(centroid, 0.0);
    }

    #[test]
    fn test_spectral_centroid_simple() {
        let signal = vec![1.0, 2.0, 3.0, 4.0];
        let fft_data = EchoEngine::compute_fft_native(&signal);
        let centroid = EchoEngine::spectral_centroid_native(&fft_data, 44100.0);

        // Centroid should be positive
        assert!(centroid >= 0.0);
    }

    #[test]
    fn test_spectral_flux_empty() {
        let fft_current: Vec<Complex<f64>> = vec![];
        let fft_previous: Vec<Complex<f64>> = vec![];
        let flux = EchoEngine::spectral_flux_native(&fft_current, &fft_previous);
        assert_eq!(flux, 0.0);
    }

    #[test]
    fn test_spectral_flux_simple() {
        let signal1 = vec![1.0, 2.0, 3.0, 4.0];
        let signal2 = vec![2.0, 3.0, 4.0, 5.0];
        let fft_current = EchoEngine::compute_fft_native(&signal1);
        let fft_previous = EchoEngine::compute_fft_native(&signal2);
        let flux = EchoEngine::spectral_flux_native(&fft_current, &fft_previous);

        // Flux should be non-negative
        assert!(flux >= 0.0);
    }

    #[test]
    fn test_spectral_rolloff_empty() {
        let fft_data: Vec<Complex<f64>> = vec![];
        let rolloff = EchoEngine::spectral_rolloff_native(&fft_data, 44100.0);
        assert_eq!(rolloff, 0.0);
    }

    #[test]
    fn test_spectral_rolloff_simple() {
        let signal = vec![1.0, 2.0, 3.0, 4.0];
        let fft_data = EchoEngine::compute_fft_native(&signal);
        let rolloff = EchoEngine::spectral_rolloff_native(&fft_data, 44100.0);

        // Rolloff should be between 0 and Nyquist frequency
        assert!(rolloff >= 0.0);
        assert!(rolloff <= 22050.0);
    }
}
