//! Physics Engine - Unified Physics Pipeline Integration
//!
//! This crate provides a unified interface for all 4 physics pipelines:
//! - CHRONOS: Frame-Timing Entropy
//! - ECHO: Acoustic Time-of-Flight
//! - IRIS: Corneal Reflection Parallax
//! - LIPSYNC: AV-Sync Drift Analysis

pub mod engine;
pub mod collector;
pub mod processor;
pub mod aggregator;
pub mod error;
pub mod logging;
pub mod monitoring;

// Re-export key types
pub use engine::PhysicsEngine;
pub use collector::{DataCollector, IrisData, LipsyncData, PhysicsData};
pub use processor::{RealTimeProcessor, ProcessedResults};
pub use aggregator::{ResultsAggregator, PhysicsResult, DetailedResults};
pub use error::{PhysicsError, ErrorHandler, ErrorContext};
pub use logging::{Logger, LogLevel, LogEntry, JsLogger};
pub use monitoring::{Monitoring, Metrics, PipelineMetrics, AlertThresholds};

// Re-export from individual pipelines
pub use iris::{SimpleFaceLandmarks, EyeLandmark, EyeType, Point2D};
pub use lipsync::{Viseme, AudioEnergy};

use wasm_bindgen::prelude::*;

/// Initialize the physics engine
#[wasm_bindgen]
pub fn init() -> Result<(), JsValue> {
    Ok(())
}

/// Get the physics engine version
#[wasm_bindgen]
pub fn version() -> String {
    "0.1.0".to_string()
}

/// Get information about the physics engine
#[wasm_bindgen]
pub fn get_info() -> JsValue {
    serde_wasm_bindgen::to_value(&serde_json::json!({
        "name": "Physics Engine",
        "version": "0.1.0",
        "pipelines": ["CHRONOS", "ECHO", "IRIS", "LIPSYNC"],
        "description": "Unified physics pipeline integration for Aegis Lens"
    })).unwrap_or(JsValue::NULL)
}
