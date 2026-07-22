//! Echo - Audio processing and speech recognition
//!
//! This module provides utilities for audio processing, speech recognition,
//! and audio-related operations.

use serde::{Deserialize, Serialize};

/// Audio data with metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioData {
    pub id: String,
    pub sample_rate: u32,
    pub channels: u16,
    pub data: Vec<f32>,
}

impl AudioData {
    /// Create new audio data
    pub fn new(id: String, sample_rate: u32, channels: u16, data: Vec<f32>) -> Self {
        Self {
            id,
            sample_rate,
            channels,
            data,
        }
    }

    /// Get duration in seconds
    pub fn duration(&self) -> f64 {
        self.data.len() as f64 / (self.sample_rate as f64 * self.channels as f64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_audio_data_creation() {
        let audio = AudioData::new("test".to_string(), 44100, 2, vec![0.0, 0.5, 1.0]);
        assert_eq!(audio.id, "test");
        assert_eq!(audio.sample_rate, 44100);
    }

    #[test]
    fn test_audio_duration() {
        let audio = AudioData::new("test".to_string(), 44100, 2, vec![0.0; 88200]);
        assert!((audio.duration() - 1.0).abs() < 0.01);
    }
}
