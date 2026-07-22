//! Chronos - Frame-Timing Entropy Physics Pipeline
//!
//! This module provides high-precision timing measurement and jitter analysis
//! for detecting virtual machine/emulator environments through frame timing entropy.
//! Compiled to WebAssembly for browser use.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use wasm_bindgen::prelude::*;

const WINDOW_SIZE: usize = 1000;
const BASELINE_MEAN: f64 = 15.0;
const BASELINE_STD: f64 = 3.0;
const THRESHOLD_CLEAR: f64 = 0.8;
const THRESHOLD_SUSPECT: f64 = 0.5;

/// Result of CHRONOS analysis
#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ChronosResult {
    pub score: f64,
    pub status: String,
    pub mean_jitter: f64,
    pub std_jitter: f64,
    pub shapiro_w: f64,
    pub kl_divergence: f64,
    pub sample_count: usize,
}

/// CHRONOS engine for timing measurement and analysis
#[wasm_bindgen]
pub struct ChronosEngine {
    samples: VecDeque<f64>,
}

impl Default for ChronosEngine {
    fn default() -> Self {
        Self::new_native()
    }
}

impl ChronosEngine {
    /// Create a new CHRONOS engine (native)
    pub fn new_native() -> Self {
        Self {
            samples: VecDeque::with_capacity(WINDOW_SIZE),
        }
    }

    /// Perform full analysis and return result (native)
    pub fn analyze_native(&self) -> ChronosResult {
        if self.samples.len() < 10 {
            return ChronosResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                mean_jitter: 0.0,
                std_jitter: 0.0,
                shapiro_w: 0.0,
                kl_divergence: 0.0,
                sample_count: self.samples.len(),
            };
        }

        let mean = self.calculate_mean();
        let std = self.calculate_std(mean);
        let shapiro_w = self.calculate_shapiro_wilk();
        let kl_divergence = self.calculate_kl_divergence(mean, std);

        let score = self.calculate_score(mean, std, shapiro_w, kl_divergence);
        let status = self.determine_status(score);

        ChronosResult {
            score,
            status,
            mean_jitter: mean,
            std_jitter: std,
            shapiro_w,
            kl_divergence,
            sample_count: self.samples.len(),
        }
    }
}

#[wasm_bindgen]
impl ChronosEngine {
    /// Create a new CHRONOS engine (WASM)
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self::new_native()
    }

    /// Measure a single timing sample
    /// Returns the jitter value in milliseconds
    #[wasm_bindgen]
    pub fn measure(&mut self) -> f64 {
        let t1 = js_sys::Date::now();
        let t2 = js_sys::Date::now();
        let jitter = t2 - t1;

        self.samples.push_back(jitter);
        if self.samples.len() > WINDOW_SIZE {
            self.samples.pop_front();
        }

        jitter
    }

    /// Measure a single timing sample (native version for testing)
    #[cfg(not(target_arch = "wasm32"))]
    pub fn measure_native(&mut self) -> f64 {
        use std::time::Instant;
        let t1 = Instant::now();
        let t2 = Instant::now();
        let jitter = t2.duration_since(t1).as_secs_f64() * 1000.0;

        self.samples.push_back(jitter);
        if self.samples.len() > WINDOW_SIZE {
            self.samples.pop_front();
        }

        jitter
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
            let result = ChronosResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                mean_jitter: 0.0,
                std_jitter: 0.0,
                shapiro_w: 0.0,
                kl_divergence: 0.0,
                sample_count: self.samples.len(),
            };
            return serde_wasm_bindgen::to_value(&result).unwrap();
        }

        let mean = self.calculate_mean();
        let std = self.calculate_std(mean);
        let shapiro_w = self.calculate_shapiro_wilk();
        let kl_divergence = self.calculate_kl_divergence(mean, std);

        let score = self.calculate_score(mean, std, shapiro_w, kl_divergence);
        let status = self.determine_status(score);

        let result = ChronosResult {
            score,
            status,
            mean_jitter: mean,
            std_jitter: std,
            shapiro_w,
            kl_divergence,
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

    fn calculate_shapiro_wilk(&self) -> f64 {
        let n = self.samples.len() as f64;
        if n < 3.0 {
            return 1.0;
        }

        let mean = self.calculate_mean();
        let sorted: Vec<f64> = {
            let mut v: Vec<f64> = self.samples.iter().cloned().collect();
            v.sort_by(|a, b| a.partial_cmp(b).unwrap());
            v
        };

        // Simplified Shapiro-Francia approximation for WASM performance
        let numerator: f64 = sorted
            .iter()
            .enumerate()
            .map(|(i, &x)| {
                let expected = (i as f64 + 0.5) / n;
                let z_score = self.normal_inv_cdf(expected);
                z_score * x
            })
            .sum::<f64>()
            .powi(2);

        let denominator: f64 = sorted.iter().map(|&x| (x - mean).powi(2)).sum();

        if denominator < 1e-10 {
            return 1.0;
        }
        (numerator / denominator).clamp(0.0, 1.0)
    }

    fn normal_inv_cdf(&self, p: f64) -> f64 {
        // Beasley-Springer-Moro approximation for inverse normal CDF
        if p <= 0.0 || p >= 1.0 {
            return 0.0;
        }

        let q = p - 0.5;
        if q.abs() < 0.425 {
            let r = 0.180625 - q * q;
            q * (((((r * 2509.0809287301726 + 33430.055461283605) * r + 67265.77102700708) * r
                + 45921.95393154974)
                * r
                + 13731.69376550946)
                * r
                + 1971.59093630605)
                / (((((r * 74545.60070509062 + 3160.0276147714) * r + 645.3837242968362) * r
                    + 64.25398732275436)
                    * r
                    + 2.506628277459239)
                    * r
                    + 1.0)
        } else {
            let r = if q <= 0.0 { p } else { 1.0 - p };
            let r = (-r.ln()).sqrt();
            let sign = if q <= 0.0 { -1.0 } else { 1.0 };
            sign * (((((r * 2.506628277459239 + 18.415189774310226) * r + 41.39119773534693) * r
                + 25.441070498102005)
                * r
                + 8.573328740300752)
                * r
                + 2.506628277459239)
                / (((((r * 1.421413741165613 + 2.754280290577424) * r + 1.932026905652153) * r
                    + 2.767668024802236)
                    * r
                    + 3.530889347551922)
                    * r
                    + 2.506628277459239)
        }
    }

    fn calculate_kl_divergence(&self, mean: f64, std: f64) -> f64 {
        let sigma1 = std;
        let sigma2 = BASELINE_STD;
        let mu1 = mean;
        let mu2 = BASELINE_MEAN;

        if sigma1 < 1e-10 || sigma2 < 1e-10 {
            return 1.0;
        }

        let term1 = (sigma2 / sigma1).ln();
        let term2 = (sigma1.powi(2) + (mu1 - mu2).powi(2)) / (2.0 * sigma2.powi(2));
        let result = term1 + term2 - 0.5;
        result.max(0.0)
    }

    fn calculate_score(&self, mean: f64, std: f64, shapiro_w: f64, kl_divergence: f64) -> f64 {
        let mut score: f64 = 1.0;

        if shapiro_w < 0.95 {
            score -= 0.5;
        }

        if kl_divergence > 0.5 {
            score -= 0.5;
        }

        if !(0.1..=50.0).contains(&mean) {
            score -= 0.3;
        }

        if !(0.5..=10.0).contains(&std) {
            score -= 0.2;
        }

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
        let engine = ChronosEngine::new_native();
        assert_eq!(engine.sample_count(), 0);
    }

    #[test]
    fn test_measure() {
        let mut engine = ChronosEngine::new_native();
        let sample = engine.measure_native();
        assert!(sample >= 0.0);
        assert_eq!(engine.sample_count(), 1);
    }

    #[test]
    fn test_capacity() {
        let mut engine = ChronosEngine::new_native();
        for _ in 0..1001 {
            engine.measure_native();
        }
        assert_eq!(engine.sample_count(), 1000);
    }

    #[test]
    fn test_clear() {
        let mut engine = ChronosEngine::new_native();
        for _ in 0..10 {
            engine.measure_native();
        }
        assert_eq!(engine.sample_count(), 10);
        engine.clear();
        assert_eq!(engine.sample_count(), 0);
    }

    #[test]
    fn test_insufficient_data() {
        let engine = ChronosEngine::new_native();
        let result = engine.analyze_native();
        assert_eq!(result.status, "INSUFFICIENT_DATA");
    }

    #[test]
    fn test_mean_calculation() {
        let mut engine = ChronosEngine::new_native();
        for _ in 0..100 {
            engine.measure_native();
        }
        let result = engine.analyze_native();
        assert!(result.mean_jitter >= 0.0);
    }
}
