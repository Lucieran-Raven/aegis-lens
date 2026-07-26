//! Lipsync - AV-Sync Drift Analysis (WASM)
//!
//! This module provides audio-visual synchronization analysis for lip-sync detection,
//! compiled to WebAssembly for browser use.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use wasm_bindgen::prelude::*;

/// Viseme (mouth shape) representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Viseme {
    pub id: u8,
    pub confidence: f32,
    pub timestamp: f64,
}

impl Viseme {
    pub fn new(id: u8, confidence: f32, timestamp: f64) -> Self {
        Self {
            id,
            confidence,
            timestamp,
        }
    }
}

/// Audio energy measurement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioEnergy {
    pub energy: f32,
    pub frequency: f32,
    pub timestamp: f64,
}

impl AudioEnergy {
    pub fn new(energy: f32, frequency: f32, timestamp: f64) -> Self {
        Self {
            energy,
            frequency,
            timestamp,
        }
    }
}

/// Cross-spectral density result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CrossSpectralDensity {
    pub magnitude: f32,
    pub phase: f32,
    pub frequency: f32,
}

impl CrossSpectralDensity {
    pub fn new(magnitude: f32, phase: f32, frequency: f32) -> Self {
        Self {
            magnitude,
            phase,
            frequency,
        }
    }
}

/// Lip-sync analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LipSyncResult {
    pub sync_score: f32,
    pub confidence: f32,
    pub drift_ms: f32,
    pub is_synced: bool,
    pub timestamp: f64,
}

impl LipSyncResult {
    pub fn new(
        sync_score: f32,
        confidence: f32,
        drift_ms: f32,
        is_synced: bool,
        timestamp: f64,
    ) -> Self {
        Self {
            sync_score,
            confidence,
            drift_ms,
            is_synced,
            timestamp,
        }
    }

    pub fn is_reliable(&self) -> bool {
        self.confidence > 0.7
    }
}

/// Lipsync Engine for AV-sync analysis
pub struct LipsyncEngine {
    viseme_buffer: VecDeque<Viseme>,
    audio_buffer: VecDeque<AudioEnergy>,
    window_size: usize,
    sample_rate: f32,
}

impl LipsyncEngine {
    pub fn new(window_size: usize, sample_rate: f32) -> Self {
        Self {
            viseme_buffer: VecDeque::with_capacity(window_size),
            audio_buffer: VecDeque::with_capacity(window_size),
            window_size,
            sample_rate,
        }
    }

    /// Extract viseme from facial landmarks (simplified)
    pub fn extract_viseme(
        &mut self,
        mouth_openness: f32,
        mouth_width: f32,
        timestamp: f64,
    ) -> Viseme {
        // Simplified viseme mapping based on mouth features
        let viseme_id = if mouth_openness > 0.5 {
            if mouth_width > 0.6 {
                10
            } else {
                11
            } // Open mouth variations
        } else if mouth_width > 0.5 {
            5
        } else {
            0
        }; // Closed mouth variations

        let viseme = Viseme::new(viseme_id, 0.8, timestamp);

        self.viseme_buffer.push_back(viseme.clone());
        if self.viseme_buffer.len() > self.window_size {
            self.viseme_buffer.pop_front();
        }

        viseme
    }

    /// Extract audio energy from audio data
    pub fn extract_audio_energy(&mut self, audio_data: &[f32], timestamp: f64) -> AudioEnergy {
        let energy: f32 = audio_data.iter().map(|&x| x * x).sum::<f32>() / audio_data.len() as f32;
        let energy = energy.sqrt();

        // Estimate dominant frequency (simplified)
        let frequency = self.estimate_frequency(audio_data);

        let audio_energy = AudioEnergy::new(energy, frequency, timestamp);

        self.audio_buffer.push_back(audio_energy.clone());
        if self.audio_buffer.len() > self.window_size {
            self.audio_buffer.pop_front();
        }

        audio_energy
    }

    /// Estimate dominant frequency from audio data
    fn estimate_frequency(&self, audio_data: &[f32]) -> f32 {
        if audio_data.len() < 2 {
            return 0.0;
        }

        // Simplified zero-crossing rate for frequency estimation
        let mut zero_crossings = 0;
        for i in 1..audio_data.len() {
            if (audio_data[i] >= 0.0) != (audio_data[i - 1] >= 0.0) {
                zero_crossings += 1;
            }
        }

        let zero_crossing_rate = zero_crossings as f32 / audio_data.len() as f32;
        zero_crossing_rate * self.sample_rate / 2.0
    }

    /// Calculate cross-spectral density between viseme and audio
    pub fn calculate_cross_spectral_density(&self) -> Option<CrossSpectralDensity> {
        if self.viseme_buffer.len() < 2 || self.audio_buffer.len() < 2 {
            return None;
        }

        // Simplified cross-correlation as proxy for cross-spectral density
        let viseme_energy: f32 = self.viseme_buffer.iter().map(|v| v.confidence).sum::<f32>();
        let audio_energy: f32 = self.audio_buffer.iter().map(|a| a.energy).sum::<f32>();

        if viseme_energy == 0.0 || audio_energy == 0.0 {
            return None;
        }

        let magnitude = (viseme_energy * audio_energy).sqrt() / (self.viseme_buffer.len() as f32);
        let phase = 0.0; // Simplified - would need FFT for actual phase
        let frequency = self.audio_buffer.iter().map(|a| a.frequency).sum::<f32>()
            / self.audio_buffer.len() as f32;

        Some(CrossSpectralDensity::new(magnitude, phase, frequency))
    }

    /// Calculate sync score based on viseme-audio alignment
    pub fn calculate_sync_score(&self) -> LipSyncResult {
        let csd = self.calculate_cross_spectral_density();

        let (sync_score, confidence, drift_ms) = if let Some(csd) = csd {
            // Calculate drift based on timestamp differences
            let drift = self.calculate_drift();

            // Sync score based on cross-spectral magnitude and drift
            let score = (csd.magnitude * 0.7 + (1.0 - drift.min(1.0)) * 0.3).min(1.0);
            let conf = if csd.magnitude > 0.5 { 0.9 } else { 0.6 };

            (score, conf, drift * 1000.0) // Convert to milliseconds
        } else {
            (0.0, 0.0, 0.0)
        };

        let is_synced = sync_score > 0.6 && confidence > 0.7;
        let timestamp = js_sys::Date::now();

        LipSyncResult::new(sync_score, confidence, drift_ms, is_synced, timestamp)
    }

    /// Calculate time drift between viseme and audio
    fn calculate_drift(&self) -> f32 {
        if self.viseme_buffer.is_empty() || self.audio_buffer.is_empty() {
            return 0.0;
        }

        let viseme_time = self.viseme_buffer.back().unwrap().timestamp;
        let audio_time = self.audio_buffer.back().unwrap().timestamp;

        (viseme_time - audio_time).abs() as f32 / 1000.0 // Normalize to seconds
    }

    /// Clear buffers
    pub fn clear(&mut self) {
        self.viseme_buffer.clear();
        self.audio_buffer.clear();
    }

    /// Get buffer sizes
    pub fn buffer_sizes(&self) -> (usize, usize) {
        (self.viseme_buffer.len(), self.audio_buffer.len())
    }
}

impl Default for LipsyncEngine {
    fn default() -> Self {
        Self::new(100, 44100.0)
    }
}

#[wasm_bindgen]
pub struct LipsyncWrapper {
    engine: LipsyncEngine,
}

#[wasm_bindgen]
impl LipsyncWrapper {
    #[wasm_bindgen(constructor)]
    pub fn new(window_size: usize, sample_rate: f32) -> LipsyncWrapper {
        LipsyncWrapper {
            engine: LipsyncEngine::new(window_size, sample_rate),
        }
    }

    #[wasm_bindgen]
    pub fn extract_viseme(&mut self, mouth_openness: f32, mouth_width: f32) -> JsValue {
        let timestamp = js_sys::Date::now();
        let viseme = self
            .engine
            .extract_viseme(mouth_openness, mouth_width, timestamp);
        serde_wasm_bindgen::to_value(&viseme).unwrap()
    }

    #[wasm_bindgen]
    pub fn extract_audio_energy(&mut self, audio_data: Vec<f32>) -> JsValue {
        let timestamp = js_sys::Date::now();
        let energy = self.engine.extract_audio_energy(&audio_data, timestamp);
        serde_wasm_bindgen::to_value(&energy).unwrap()
    }

    #[wasm_bindgen]
    pub fn calculate_sync_score(&mut self) -> JsValue {
        let result = self.engine.calculate_sync_score();
        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    #[wasm_bindgen]
    pub fn clear(&mut self) {
        self.engine.clear();
    }

    #[wasm_bindgen]
    pub fn buffer_sizes(&self) -> Vec<usize> {
        let (viseme, audio) = self.engine.buffer_sizes();
        vec![viseme, audio]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lipsync_engine_creation() {
        let engine = LipsyncEngine::new(100, 44100.0);
        assert_eq!(engine.window_size, 100);
        assert_eq!(engine.sample_rate, 44100.0);
    }

    #[test]
    fn test_viseme_extraction() {
        let mut engine = LipsyncEngine::new(10, 44100.0);
        let viseme = engine.extract_viseme(0.6, 0.7, 1000.0);
        assert_eq!(viseme.confidence, 0.8);
        assert_eq!(engine.viseme_buffer.len(), 1);
    }

    #[test]
    fn test_audio_energy_extraction() {
        let mut engine = LipsyncEngine::new(10, 44100.0);
        let audio_data = vec![0.5, -0.3, 0.8, -0.2, 0.1];
        let energy = engine.extract_audio_energy(&audio_data, 1000.0);
        assert!(energy.energy > 0.0);
        assert_eq!(engine.audio_buffer.len(), 1);
    }

    #[test]
    fn test_buffer_limits() {
        let mut engine = LipsyncEngine::new(5, 44100.0);
        for i in 0..10 {
            engine.extract_viseme(0.5, 0.5, i as f64);
        }
        assert_eq!(engine.viseme_buffer.len(), 5);
    }

    #[test]
    fn test_sync_score_calculation() {
        let mut engine = LipsyncEngine::new(10, 44100.0);

        // Add some viseme data
        for i in 0..5 {
            engine.extract_viseme(0.5 + (i as f32 * 0.1), 0.6, i as f64 * 100.0);
        }

        // Add some audio data
        for i in 0..5 {
            let audio_data = vec![0.5, -0.3, 0.8];
            engine.extract_audio_energy(&audio_data, i as f64 * 100.0);
        }

        // Test cross-spectral density calculation instead (doesn't use js_sys)
        let csd = engine.calculate_cross_spectral_density();
        assert!(csd.is_some());
        let csd = csd.unwrap();
        assert!(csd.magnitude >= 0.0);
    }

    #[test]
    fn test_clear_buffers() {
        let mut engine = LipsyncEngine::new(10, 44100.0);
        engine.extract_viseme(0.5, 0.5, 1000.0);
        engine.clear();
        assert_eq!(engine.viseme_buffer.len(), 0);
        assert_eq!(engine.audio_buffer.len(), 0);
    }

    #[test]
    fn test_default_engine() {
        let engine = LipsyncEngine::default();
        assert_eq!(engine.window_size, 100);
        assert_eq!(engine.sample_rate, 44100.0);
    }
}
