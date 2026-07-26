//! Physics Engine - Unified Physics Pipeline Integration
//!
//! This crate provides a unified interface for all 4 physics pipelines:
//! - CHRONOS: Frame-Timing Entropy
//! - ECHO: Acoustic Time-of-Flight
//! - IRIS: Corneal Reflection Parallax
//! - LIPSYNC: AV-Sync Drift Analysis

pub mod aggregator;
pub mod collector;
pub mod engine;
pub mod error;
pub mod logging;
pub mod monitoring;
pub mod processor;

// Re-export key types
pub use aggregator::{DetailedResults, PhysicsResult, ResultsAggregator};
pub use collector::{DataCollector, IrisData, LipsyncData, PhysicsData};
pub use engine::PhysicsEngine;
pub use error::{ErrorContext, ErrorHandler, PhysicsError};
pub use logging::{JsLogger, LogEntry, LogLevel, Logger};
pub use monitoring::{AlertThresholds, Metrics, Monitoring, PipelineMetrics};
pub use processor::{ProcessedResults, RealTimeProcessor};

// Re-export from individual pipelines
pub use iris::{EyeLandmark, EyeType, Point2D, SimpleFaceLandmarks};
pub use lipsync::{AudioEnergy, Viseme};

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
    }))
    .unwrap_or(JsValue::NULL)
}
