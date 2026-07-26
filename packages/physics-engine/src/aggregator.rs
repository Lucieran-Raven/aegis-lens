//! Results Aggregation
//!
//! This module provides results aggregation from all 4 physics pipelines
//! with weighted scoring and unified status determination.

use crate::ProcessedResults;
use serde::{Deserialize, Serialize};

/// Detailed results from all pipelines
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DetailedResults {
    pub chronos_score: f64,
    pub echo_score: f64,
    pub iris_score: f64,
    pub lipsync_score: f64,
    pub status: String,
}

/// Combined physics result
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

/// Results aggregator
pub struct ResultsAggregator {
    chronos_score: f64,
    echo_score: f64,
    iris_score: f64,
    lipsync_score: f64,
    combined_score: f64,
    status: String,
    chronos_weight: f64,
    echo_weight: f64,
    iris_weight: f64,
    lipsync_weight: f64,
}

impl ResultsAggregator {
    /// Create a new results aggregator
    pub fn new() -> Self {
        Self {
            chronos_score: 0.0,
            echo_score: 0.0,
            iris_score: 0.0,
            lipsync_score: 0.0,
            combined_score: 0.0,
            status: "INSUFFICIENT_DATA".to_string(),
            chronos_weight: 0.25,
            echo_weight: 0.25,
            iris_weight: 0.25,
            lipsync_weight: 0.25,
        }
    }

    /// Aggregate processed results
    pub fn aggregate(&mut self, results: ProcessedResults) -> PhysicsResult {
        self.chronos_score = results.chronos.score;
        self.echo_score = results.echo.score;
        self.iris_score = results.iris.score;
        self.lipsync_score = results.lipsync.sync_score as f64;

        self.combined_score = self.chronos_score * self.chronos_weight
            + self.echo_score * self.echo_weight
            + self.iris_score * self.iris_weight
            + self.lipsync_score * self.lipsync_weight;

        self.status = self.determine_status();

        PhysicsResult {
            combined_score: self.combined_score,
            combined_status: self.status.clone(),
            chronos_score: self.chronos_score,
            echo_score: self.echo_score,
            iris_score: self.iris_score,
            lipsync_score: self.lipsync_score,
        }
    }

    /// Determine status based on scores
    fn determine_status(&self) -> String {
        if self.combined_score > 0.8 {
            "CLEAR".to_string()
        } else if self.combined_score > 0.5 {
            "SUSPECT".to_string()
        } else {
            "ANOMALY".to_string()
        }
    }

    /// Get combined score
    pub fn get_combined_score(&self) -> f64 {
        self.combined_score
    }

    /// Get status
    pub fn get_status(&self) -> String {
        self.status.clone()
    }

    /// Get detailed results
    pub fn get_detailed_results(&self) -> DetailedResults {
        DetailedResults {
            chronos_score: self.chronos_score,
            echo_score: self.echo_score,
            iris_score: self.iris_score,
            lipsync_score: self.lipsync_score,
            status: self.status.clone(),
        }
    }

    /// Get weights
    pub fn get_weights(&self) -> (f64, f64, f64, f64) {
        (
            self.chronos_weight,
            self.echo_weight,
            self.iris_weight,
            self.lipsync_weight,
        )
    }

    /// Set custom weights (must sum to 1.0)
    pub fn set_weights(&mut self, chronos: f64, echo: f64, iris: f64, lipsync: f64) {
        let sum = chronos + echo + iris + lipsync;
        assert!((sum - 1.0).abs() < 0.001, "Weights must sum to 1.0");

        self.chronos_weight = chronos;
        self.echo_weight = echo;
        self.iris_weight = iris;
        self.lipsync_weight = lipsync;
    }

    /// Reset aggregator
    pub fn reset(&mut self) {
        self.chronos_score = 0.0;
        self.echo_score = 0.0;
        self.iris_score = 0.0;
        self.lipsync_score = 0.0;
        self.combined_score = 0.0;
        self.status = "INSUFFICIENT_DATA".to_string();
    }
}

impl Default for ResultsAggregator {
    fn default() -> Self {
        Self::new()
    }
}
