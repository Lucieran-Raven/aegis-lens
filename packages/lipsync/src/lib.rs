//! Lipsync - Lip-sync detection and analysis (WASM)
//!
//! This module provides utilities for lip-sync detection and analysis,
//! compiled to WebAssembly for browser use.

use serde::{Deserialize, Serialize};

/// Lip-sync analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LipSyncResult {
    pub confidence: f32,
    pub timestamp: f64,
    pub is_synced: bool,
}

impl LipSyncResult {
    /// Create a new lip-sync result
    pub fn new(confidence: f32, timestamp: f64, is_synced: bool) -> Self {
        Self {
            confidence,
            timestamp,
            is_synced,
        }
    }

    /// Check if the result is reliable
    pub fn is_reliable(&self) -> bool {
        self.confidence > 0.7
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lipsync_result_creation() {
        let result = LipSyncResult::new(0.85, 1.5, true);
        assert_eq!(result.confidence, 0.85);
        assert!(result.is_synced);
    }

    #[test]
    fn test_lipsync_reliable() {
        let reliable = LipSyncResult::new(0.85, 1.5, true);
        assert!(reliable.is_reliable());

        let unreliable = LipSyncResult::new(0.5, 1.5, false);
        assert!(!unreliable.is_reliable());
    }
}
