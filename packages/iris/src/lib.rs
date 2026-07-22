//! Iris - Computer vision and facial analysis
//!
//! This module provides utilities for computer vision, facial recognition,
//! and image processing operations.

use serde::{Deserialize, Serialize};

/// Image metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImageMetadata {
    pub id: String,
    pub width: u32,
    pub height: u32,
    pub format: String,
}

impl ImageMetadata {
    /// Create new image metadata
    pub fn new(id: String, width: u32, height: u32, format: String) -> Self {
        Self {
            id,
            width,
            height,
            format,
        }
    }

    /// Get total pixel count
    pub fn pixel_count(&self) -> u64 {
        self.width as u64 * self.height as u64
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_image_metadata_creation() {
        let meta = ImageMetadata::new("test".to_string(), 1920, 1080, "RGB".to_string());
        assert_eq!(meta.id, "test");
        assert_eq!(meta.width, 1920);
    }

    #[test]
    fn test_pixel_count() {
        let meta = ImageMetadata::new("test".to_string(), 1920, 1080, "RGB".to_string());
        assert_eq!(meta.pixel_count(), 1920 * 1080);
    }
}
