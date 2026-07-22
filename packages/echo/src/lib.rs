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
}
