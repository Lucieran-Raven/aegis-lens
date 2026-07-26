//! Data Collection Pipeline
//!
//! This module provides a unified data collection pipeline that collects data
//! from all 4 physics pipelines simultaneously with synchronized timestamps.

use iris::SimpleFaceLandmarks;
use lipsync::{AudioEnergy, Viseme};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

/// IRIS data for collection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IrisData {
    pub face_landmarks: Option<SimpleFaceLandmarks>,
    pub face_detected: bool,
    pub eye_variance: f32,
    pub timestamp: u64,
}

impl IrisData {
    pub fn new(
        face_landmarks: Option<SimpleFaceLandmarks>,
        face_detected: bool,
        eye_variance: f32,
    ) -> Self {
        Self {
            face_landmarks,
            face_detected,
            eye_variance,
            timestamp: Self::get_timestamp(),
        }
    }

    #[cfg(target_arch = "wasm32")]
    fn get_timestamp() -> u64 {
        js_sys::Date::now() as u64
    }

    #[cfg(not(target_arch = "wasm32"))]
    fn get_timestamp() -> u64 {
        0u64
    }
}

/// LIPSYNC data for collection
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LipsyncData {
    pub viseme: Option<Viseme>,
    pub audio_energy: Option<AudioEnergy>,
    pub sync_score: f32,
    pub timestamp: u64,
}

impl LipsyncData {
    pub fn new(viseme: Option<Viseme>, audio_energy: Option<AudioEnergy>, sync_score: f32) -> Self {
        Self {
            viseme,
            audio_energy,
            sync_score,
            timestamp: Self::get_timestamp(),
        }
    }

    #[cfg(target_arch = "wasm32")]
    fn get_timestamp() -> u64 {
        js_sys::Date::now() as u64
    }

    #[cfg(not(target_arch = "wasm32"))]
    fn get_timestamp() -> u64 {
        0u64
    }
}

/// Data collector for all 4 pipelines
pub struct DataCollector {
    chronos_buffer: VecDeque<f64>,
    echo_buffer: VecDeque<f32>,
    iris_buffer: VecDeque<IrisData>,
    lipsync_buffer: VecDeque<LipsyncData>,
    timestamp: u64,
}

impl DataCollector {
    /// Create a new data collector
    pub fn new() -> Self {
        #[cfg(target_arch = "wasm32")]
        let timestamp = js_sys::Date::now() as u64;
        #[cfg(not(target_arch = "wasm32"))]
        let timestamp = 0u64;

        Self {
            chronos_buffer: VecDeque::with_capacity(1000),
            echo_buffer: VecDeque::with_capacity(100),
            iris_buffer: VecDeque::with_capacity(100),
            lipsync_buffer: VecDeque::with_capacity(100),
            timestamp,
        }
    }

    /// Collect CHRONOS timing sample
    pub fn collect_chronos(&mut self, sample: f64) {
        self.chronos_buffer.push_back(sample);
        if self.chronos_buffer.len() > 1000 {
            self.chronos_buffer.pop_front();
        }
    }

    /// Collect ECHO timing sample
    pub fn collect_echo(&mut self, sample: f32) {
        self.echo_buffer.push_back(sample);
        if self.echo_buffer.len() > 100 {
            self.echo_buffer.pop_front();
        }
    }

    /// Collect IRIS data
    pub fn collect_iris(&mut self, data: IrisData) {
        self.iris_buffer.push_back(data);
        if self.iris_buffer.len() > 100 {
            self.iris_buffer.pop_front();
        }
    }

    /// Collect LIPSYNC data
    pub fn collect_lipsync(&mut self, data: LipsyncData) {
        self.lipsync_buffer.push_back(data);
        if self.lipsync_buffer.len() > 100 {
            self.lipsync_buffer.pop_front();
        }
    }

    /// Get all collected data
    pub fn get_all_data(&self) -> PhysicsData {
        PhysicsData {
            chronos_samples: self.chronos_buffer.iter().cloned().collect(),
            echo_samples: self.echo_buffer.iter().cloned().collect(),
            iris_data: self.iris_buffer.iter().cloned().collect(),
            lipsync_data: self.lipsync_buffer.iter().cloned().collect(),
        }
    }

    /// Get CHRONOS samples
    pub fn get_chronos_samples(&self) -> Vec<f64> {
        self.chronos_buffer.iter().cloned().collect()
    }

    /// Get ECHO samples
    pub fn get_echo_samples(&self) -> Vec<f32> {
        self.echo_buffer.iter().cloned().collect()
    }

    /// Get IRIS data
    pub fn get_iris_data(&self) -> Vec<IrisData> {
        self.iris_buffer.iter().cloned().collect()
    }

    /// Get LIPSYNC data
    pub fn get_lipsync_data(&self) -> Vec<LipsyncData> {
        self.lipsync_buffer.iter().cloned().collect()
    }

    /// Get buffer sizes
    pub fn get_buffer_sizes(&self) -> (usize, usize, usize, usize) {
        (
            self.chronos_buffer.len(),
            self.echo_buffer.len(),
            self.iris_buffer.len(),
            self.lipsync_buffer.len(),
        )
    }

    /// Check if data is synchronized (within 100ms)
    pub fn is_synchronized(&self) -> bool {
        if self.iris_buffer.is_empty() || self.lipsync_buffer.is_empty() {
            return false;
        }

        let iris_time = self.iris_buffer.back().map(|d| d.timestamp).unwrap_or(0);
        let lipsync_time = self.lipsync_buffer.back().map(|d| d.timestamp).unwrap_or(0);

        (iris_time as i64 - lipsync_time as i64).abs() < 100
    }

    /// Clear all buffers
    pub fn clear(&mut self) {
        self.chronos_buffer.clear();
        self.echo_buffer.clear();
        self.iris_buffer.clear();
        self.lipsync_buffer.clear();
        self.timestamp = Self::get_timestamp();
    }

    #[cfg(target_arch = "wasm32")]
    fn get_timestamp() -> u64 {
        js_sys::Date::now() as u64
    }

    #[cfg(not(target_arch = "wasm32"))]
    fn get_timestamp() -> u64 {
        0u64
    }
}

/// Physics data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhysicsData {
    pub chronos_samples: Vec<f64>,
    pub echo_samples: Vec<f32>,
    pub iris_data: Vec<IrisData>,
    pub lipsync_data: Vec<LipsyncData>,
}

impl PhysicsData {
    pub fn new() -> Self {
        Self {
            chronos_samples: Vec::new(),
            echo_samples: Vec::new(),
            iris_data: Vec::new(),
            lipsync_data: Vec::new(),
        }
    }

    pub fn is_empty(&self) -> bool {
        self.chronos_samples.is_empty()
            && self.echo_samples.is_empty()
            && self.iris_data.is_empty()
            && self.lipsync_data.is_empty()
    }
}
