//! Physics Engine - Unified Pipeline Engine
//!
//! This module provides the unified PhysicsEngine struct that combines
//! all 4 physics pipelines (CHRONOS, ECHO, IRIS, LIPSYNC).

use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

#[cfg(target_arch = "wasm32")]
use js_sys::Date;

// Import from individual pipelines
use chronos::{ChronosEngine, ChronosResult};
use echo::{EchoEngine, EchoResult};
use iris::{IrisEngine, IrisResult};
use lipsync::LipsyncEngine;

/// Unified physics engine that combines all 4 physics pipelines
#[wasm_bindgen]
pub struct PhysicsEngine {
    chronos: ChronosEngine,
    echo: EchoEngine,
    iris: IrisEngine,
    lipsync: LipsyncEngine,
}

/// Combined result from all pipelines
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PhysicsResult {
    pub combined_score: f64,
    pub combined_status: String,
    pub chronos_score: f64,
    pub echo_score: f64,
    pub iris_score: f64,
    pub lipsync_score: f64,
}

impl Default for PhysicsEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl PhysicsEngine {
    /// Create a new physics engine
    pub fn new_native() -> Self {
        Self {
            chronos: ChronosEngine::new_native(),
            echo: EchoEngine::new_native(),
            iris: IrisEngine::new(),
            lipsync: LipsyncEngine::new(100, 44100.0),
        }
    }

    /// Analyze all pipelines and return combined result
    pub fn analyze_all_native(&self) -> PhysicsResult {
        let chronos_result = self.chronos.analyze_native();
        let echo_result = self.echo.analyze_native();
        let iris_result = self.iris.analyze();
        let lipsync_result = self.lipsync.calculate_sync_score();

        let combined_score = (chronos_result.score
            + echo_result.score
            + iris_result.score
            + lipsync_result.sync_score as f64)
            / 4.0;

        let combined_status = if combined_score > 0.8 {
            "CLEAR".to_string()
        } else if combined_score > 0.5 {
            "SUSPECT".to_string()
        } else {
            "ANOMALY".to_string()
        };

        PhysicsResult {
            combined_score,
            combined_status,
            chronos_score: chronos_result.score,
            echo_score: echo_result.score,
            iris_score: iris_result.score,
            lipsync_score: lipsync_result.sync_score as f64,
        }
    }

    /// Clear all pipeline buffers
    pub fn clear_all_native(&mut self) {
        self.chronos.clear();
        self.echo.clear();
        self.iris.clear();
        self.lipsync.clear();
    }

    /// Get CHRONOS result
    pub fn get_chronos_result_native(&self) -> ChronosResult {
        self.chronos.analyze_native()
    }

    /// Get ECHO result
    pub fn get_echo_result_native(&self) -> EchoResult {
        self.echo.analyze_native()
    }

    /// Get IRIS result
    pub fn get_iris_result_native(&self) -> IrisResult {
        self.iris.analyze()
    }

    /// Get combined score
    pub fn get_combined_score_native(&self) -> f64 {
        self.analyze_all_native().combined_score
    }

    /// Get combined status
    pub fn get_combined_status_native(&self) -> String {
        self.analyze_all_native().combined_status
    }
}

#[wasm_bindgen]
impl PhysicsEngine {
    /// Create a new physics engine (WASM constructor)
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self::new_native()
    }

    /// Measure CHRONOS timing sample
    #[wasm_bindgen]
    pub fn measure_chronos(&mut self) -> f64 {
        #[cfg(target_arch = "wasm32")]
        return self.chronos.measure();
        #[cfg(not(target_arch = "wasm32"))]
        return 0.0; // Return default value for non-WASM
    }

    /// Measure ECHO timing sample
    #[wasm_bindgen]
    pub fn measure_echo(&mut self) -> f64 {
        #[cfg(target_arch = "wasm32")]
        return self.echo.measure();
        #[cfg(not(target_arch = "wasm32"))]
        return 0.0; // Return default value for non-WASM
    }

    /// Process IRIS face data
    #[wasm_bindgen]
    pub fn process_iris(&mut self, _face_data: JsValue) -> JsValue {
        // For now, return a default result since IRIS needs image data
        // In a real implementation, this would process face landmarks
        let result = self.iris.analyze();
        serde_wasm_bindgen::to_value(&result).unwrap_or(JsValue::NULL)
    }

    /// Process LIPSYNC viseme and audio data
    #[wasm_bindgen]
    pub fn process_lipsync(&mut self, viseme: f32, audio_energy: f32) -> JsValue {
        #[cfg(target_arch = "wasm32")]
        let timestamp = Date::now();
        #[cfg(not(target_arch = "wasm32"))]
        let timestamp = 0.0;

        let _viseme_result = self.lipsync.extract_viseme(viseme, audio_energy, timestamp);
        let _audio_result = self
            .lipsync
            .extract_audio_energy(&vec![audio_energy; 100], timestamp);
        let sync_result = self.lipsync.calculate_sync_score();
        serde_wasm_bindgen::to_value(&sync_result).unwrap_or(JsValue::NULL)
    }

    /// Perform full analysis on all pipelines
    #[wasm_bindgen]
    pub fn analyze_all(&self) -> JsValue {
        let result = self.analyze_all_native();
        serde_wasm_bindgen::to_value(&result).unwrap_or(JsValue::NULL)
    }

    /// Clear all buffers
    #[wasm_bindgen]
    pub fn clear_all(&mut self) {
        self.clear_all_native();
    }

    /// Get CHRONOS result
    #[wasm_bindgen]
    pub fn get_chronos_result(&self) -> JsValue {
        let result = self.get_chronos_result_native();
        serde_wasm_bindgen::to_value(&result).unwrap_or(JsValue::NULL)
    }

    /// Get ECHO result
    #[wasm_bindgen]
    pub fn get_echo_result(&self) -> JsValue {
        let result = self.get_echo_result_native();
        serde_wasm_bindgen::to_value(&result).unwrap_or(JsValue::NULL)
    }

    /// Get IRIS result
    #[wasm_bindgen]
    pub fn get_iris_result(&self) -> JsValue {
        let result = self.get_iris_result_native();
        serde_wasm_bindgen::to_value(&result).unwrap_or(JsValue::NULL)
    }

    /// Get combined score
    #[wasm_bindgen]
    pub fn get_combined_score(&self) -> f64 {
        self.get_combined_score_native()
    }

    /// Get combined status
    #[wasm_bindgen]
    pub fn get_combined_status(&self) -> String {
        self.get_combined_status_native()
    }
}
