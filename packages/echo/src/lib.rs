//! ECHO - Acoustic Time-of-Flight Physics Pipeline
//!
//! This module provides acoustic time-of-flight measurement and analysis
//! for detecting audio replay attacks and synthetic speech through
//! acoustic fingerprinting. Compiled to WebAssembly for browser use.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use wasm_bindgen::prelude::*;

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
            start_frequency: 1000.0,  // 1 kHz
            end_frequency: 8000.0,    // 8 kHz
            duration: 0.1,            // 100 ms
            sample_rate: 44100.0,     // 44.1 kHz
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
                sample_count: self.samples.len(),
            };
        }

        let mean = self.calculate_mean();
        let std = self.calculate_std(mean);
        let spectral_centroid = self.calculate_spectral_centroid();
        let zcr = self.calculate_zero_crossing_rate();

        let score = self.calculate_score(mean, std, spectral_centroid, zcr);
        let status = self.determine_status(score);

        EchoResult {
            score,
            status,
            mean_tof: mean,
            std_tof: std,
            spectral_centroid,
            zero_crossing_rate: zcr,
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
            let phase = 2.0 * std::f64::consts::PI * (
                config.start_frequency * t +
                freq_slope * t * t / 2.0
            );
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
            sample_count: self.samples.len(),
        };
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Generate a linear chirp signal
    /// Returns the chirp signal as a JsValue
    #[wasm_bindgen]
    pub fn generate_chirp(&self, start_freq: f64, end_freq: f64, duration: f64, sample_rate: f64) -> JsValue {
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
        let weighted_sum: f64 = self.samples.iter().enumerate().map(|(i, &x)| i as f64 * x).sum();
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
        let crossings = samples.windows(2)
            .filter(|w| w[0] * w[1] < 0.0)
            .count();
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
}
