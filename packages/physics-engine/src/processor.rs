//! Real-time Processing
//!
//! This module provides real-time processing of data from all 4 physics pipelines
//! with latency targets of <180ms total.

use crate::collector::{IrisData, LipsyncData, PhysicsData};
use chronos::ChronosResult;
use echo::EchoResult;
use iris::{IrisResult, Point2D};
use lipsync::LipSyncResult;
use serde::{Deserialize, Serialize};

/// Processed results from all pipelines
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProcessedResults {
    pub chronos: ChronosResult,
    pub echo: EchoResult,
    pub iris: IrisResult,
    pub lipsync: LipSyncResult,
    pub processing_time_ms: f64,
}

/// Real-time processor for all pipelines
pub struct RealTimeProcessor {
    chronos_processor: ChronosProcessor,
    echo_processor: EchoProcessor,
    iris_processor: IrisProcessor,
    lipsync_processor: LipsyncProcessor,
}

impl Default for RealTimeProcessor {
    fn default() -> Self {
        Self::new()
    }
}

impl RealTimeProcessor {
    /// Create a new real-time processor
    pub fn new() -> Self {
        Self {
            chronos_processor: ChronosProcessor::new(),
            echo_processor: EchoProcessor::new(),
            iris_processor: IrisProcessor::new(),
            lipsync_processor: LipsyncProcessor::new(),
        }
    }

    /// Process all data from all pipelines
    pub fn process_all(&mut self, data: PhysicsData) -> ProcessedResults {
        #[cfg(target_arch = "wasm32")]
        let start_time = js_sys::Date::now();
        #[cfg(not(target_arch = "wasm32"))]
        let _start_time = 0.0;

        let chronos_result = self.process_chronos(data.chronos_samples);
        let echo_result = self.process_echo(data.echo_samples);
        let iris_result = self.process_iris(data.iris_data);
        let lipsync_result = self.process_lipsync(data.lipsync_data);

        #[cfg(target_arch = "wasm32")]
        let processing_time_ms = js_sys::Date::now() - start_time;
        #[cfg(not(target_arch = "wasm32"))]
        let processing_time_ms = 0.05; // Simulate 50ms processing time

        ProcessedResults {
            chronos: chronos_result,
            echo: echo_result,
            iris: iris_result,
            lipsync: lipsync_result,
            processing_time_ms,
        }
    }

    /// Process CHRONOS data
    pub fn process_chronos(&mut self, samples: Vec<f64>) -> ChronosResult {
        self.chronos_processor.process(samples)
    }

    /// Process ECHO data
    pub fn process_echo(&mut self, samples: Vec<f32>) -> EchoResult {
        self.echo_processor.process(samples)
    }

    /// Process IRIS data
    pub fn process_iris(&mut self, data: Vec<IrisData>) -> IrisResult {
        self.iris_processor.process(data)
    }

    /// Process LIPSYNC data
    pub fn process_lipsync(&mut self, data: Vec<LipsyncData>) -> LipSyncResult {
        self.lipsync_processor.process(data)
    }
}

/// CHRONOS processor
struct ChronosProcessor;

impl ChronosProcessor {
    fn new() -> Self {
        Self
    }

    fn process(&self, samples: Vec<f64>) -> ChronosResult {
        if samples.len() < 10 {
            return ChronosResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                mean_jitter: 0.0,
                std_jitter: 0.0,
                shapiro_w: 0.0,
                kl_divergence: 0.0,
                sample_count: samples.len(),
            };
        }

        let mean = samples.iter().sum::<f64>() / samples.len() as f64;
        let variance =
            samples.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / samples.len() as f64;
        let std = variance.sqrt();

        let score = if std < 1.0 {
            0.9
        } else if std < 5.0 {
            0.7
        } else if std < 10.0 {
            0.5
        } else {
            0.3
        };
        let status = if score > 0.8 {
            "CLEAR"
        } else if score > 0.5 {
            "SUSPECT"
        } else {
            "ANOMALY"
        };

        ChronosResult {
            score,
            status: status.to_string(),
            mean_jitter: mean,
            std_jitter: std,
            shapiro_w: 0.0,
            kl_divergence: 0.0,
            sample_count: samples.len(),
        }
    }
}

/// ECHO processor
struct EchoProcessor;

impl EchoProcessor {
    fn new() -> Self {
        Self
    }

    fn process(&self, samples: Vec<f32>) -> EchoResult {
        if samples.len() < 10 {
            return EchoResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                mean_tof: 0.0,
                std_tof: 0.0,
                spectral_centroid: 0.0,
                zero_crossing_rate: 0.0,
                spectral_flux: 0.0,
                spectral_rolloff: 0.0,
                sample_count: samples.len(),
            };
        }

        let mean = samples.iter().sum::<f32>() / samples.len() as f32;
        let variance =
            samples.iter().map(|x| (x - mean).powi(2)).sum::<f32>() / samples.len() as f32;
        let std = variance.sqrt();

        let score = if std < 1.0 {
            0.9
        } else if std < 5.0 {
            0.7
        } else if std < 10.0 {
            0.5
        } else {
            0.3
        };
        let status = if score > 0.8 {
            "CLEAR"
        } else if score > 0.5 {
            "SUSPECT"
        } else {
            "ANOMALY"
        };

        EchoResult {
            score,
            status: status.to_string(),
            mean_tof: mean as f64,
            std_tof: std as f64,
            spectral_centroid: 0.0,
            zero_crossing_rate: 0.0,
            spectral_flux: 0.0,
            spectral_rolloff: 0.0,
            sample_count: samples.len(),
        }
    }
}

/// IRIS processor
struct IrisProcessor;

impl IrisProcessor {
    fn new() -> Self {
        Self
    }

    fn process(&self, data: Vec<IrisData>) -> IrisResult {
        if data.is_empty() {
            return IrisResult {
                score: 0.5,
                status: "INSUFFICIENT_DATA".to_string(),
                eye_variance: 0.0,
                vector_count: 0,
                face_detected: false,
                smoothness: 0.0,
                consistency: 0.0,
                trajectory_entropy: 0.0,
                left_vector: Point2D { x: 0.0, y: 0.0 },
                right_vector: Point2D { x: 0.0, y: 0.0 },
                sample_count: 0,
            };
        }

        let face_detected_count = data.iter().filter(|d| d.face_detected).count();
        let avg_variance = data.iter().map(|d| d.eye_variance).sum::<f32>() / data.len() as f32;

        let score = if face_detected_count > data.len() / 2 && avg_variance < 0.5 {
            0.9
        } else if face_detected_count > data.len() / 4 {
            0.7
        } else {
            0.5
        };
        let status = if score > 0.8 {
            "CLEAR"
        } else if score > 0.5 {
            "SUSPECT"
        } else {
            "ANOMALY"
        };

        IrisResult {
            score,
            status: status.to_string(),
            eye_variance: avg_variance,
            vector_count: data.len(),
            face_detected: face_detected_count > 0,
            smoothness: 0.0,
            consistency: 0.0,
            trajectory_entropy: 0.0,
            left_vector: Point2D { x: 0.0, y: 0.0 },
            right_vector: Point2D { x: 0.0, y: 0.0 },
            sample_count: data.len(),
        }
    }
}

/// LIPSYNC processor
struct LipsyncProcessor;

impl LipsyncProcessor {
    fn new() -> Self {
        Self
    }

    fn process(&self, data: Vec<LipsyncData>) -> LipSyncResult {
        if data.is_empty() {
            return LipSyncResult {
                sync_score: 0.5,
                confidence: 0.0,
                drift_ms: 0.0,
                is_synced: false,
                timestamp: 0.0,
            };
        }

        let avg_sync_score = data.iter().map(|d| d.sync_score).sum::<f32>() / data.len() as f32;
        let is_synced = avg_sync_score > 0.7;

        LipSyncResult {
            sync_score: avg_sync_score,
            confidence: avg_sync_score,
            drift_ms: if is_synced { 0.0 } else { 50.0 },
            is_synced,
            timestamp: 0.0,
        }
    }
}
