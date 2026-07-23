//! Iris - Computer vision and facial analysis
//!
//! This module provides utilities for computer vision, facial recognition,
//! and image processing operations.

use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

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

/// Face detection result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen]
pub struct FaceDetection {
    pub x: f32,
    pub y: f32,
    pub width: f32,
    pub height: f32,
    pub confidence: f32,
}

impl FaceDetection {
    /// Create new face detection
    pub fn new(x: f32, y: f32, width: f32, height: f32, confidence: f32) -> Self {
        Self {
            x,
            y,
            width,
            height,
            confidence,
        }
    }
}

/// Eye landmark
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen]
pub struct EyeLandmark {
    pub x: f32,
    pub y: f32,
    pub eye_type: EyeType,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[wasm_bindgen]
pub enum EyeType {
    Left,
    Right,
}

/// Face landmarks
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FaceLandmarks {
    pub left_eye: EyeLandmark,
    pub right_eye: EyeLandmark,
    pub nose: (f32, f32),
    pub mouth: (f32, f32),
}

/// IRIS analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen(getter_with_clone)]
pub struct IrisResult {
    pub score: f64,
    pub status: String,
    pub eye_variance: f32,
    pub vector_count: usize,
    pub face_detected: bool,
}

/// IRIS engine for face detection and analysis
#[wasm_bindgen]
pub struct IrisEngine {
    detections: Vec<FaceDetection>,
    eye_vectors: Vec<(f32, f32)>,
}

#[wasm_bindgen]
impl IrisEngine {
    /// Create new IRIS engine
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self {
            detections: Vec::new(),
            eye_vectors: Vec::new(),
        }
    }

    /// Detect faces from image data (simplified for WASM)
    /// In production, this would integrate with MediaPipe or similar
    pub fn detect_faces(&mut self, _image_data: &[u8], _width: u32, _height: u32) -> Vec<FaceDetection> {
        // Simplified face detection using skin tone regions
        // This is a placeholder - production would use MediaPipe Face Detection
        self.detections.clear();
        
        // For now, return empty detection
        // Real implementation would use MediaPipe Face Detection API
        Vec::new()
    }

    /// Get current face detections
    pub fn get_detections(&self) -> Vec<FaceDetection> {
        self.detections.clone()
    }

    /// Clear all detections
    pub fn clear(&mut self) {
        self.detections.clear();
        self.eye_vectors.clear();
    }

    /// Track eye vector movement
    pub fn track_eye_vector(&mut self, left_eye: &EyeLandmark, right_eye: &EyeLandmark) {
        // Calculate vector between eyes
        let dx = right_eye.x - left_eye.x;
        let dy = right_eye.y - left_eye.y;
        
        self.eye_vectors.push((dx, dy));
        
        // Keep only last 100 vectors
        if self.eye_vectors.len() > 100 {
            self.eye_vectors.remove(0);
        }
    }

    /// Calculate eye movement variance
    pub fn calculate_eye_variance(&self) -> f32 {
        if self.eye_vectors.len() < 2 {
            return 0.0;
        }
        
        let mean_x: f32 = self.eye_vectors.iter().map(|v| v.0).sum::<f32>() / self.eye_vectors.len() as f32;
        let mean_y: f32 = self.eye_vectors.iter().map(|v| v.1).sum::<f32>() / self.eye_vectors.len() as f32;
        
        let variance_x: f32 = self.eye_vectors.iter()
            .map(|v| (v.0 - mean_x).powi(2))
            .sum::<f32>() / self.eye_vectors.len() as f32;
        
        let variance_y: f32 = self.eye_vectors.iter()
            .map(|v| (v.1 - mean_y).powi(2))
            .sum::<f32>() / self.eye_vectors.len() as f32;
        
        (variance_x + variance_y).sqrt()
    }

    /// Analyze eye movement and calculate liveness score
    pub fn analyze(&self) -> IrisResult {
        const THRESHOLD_CLEAR: f64 = 0.8;
        const THRESHOLD_SUSPECT: f64 = 0.5;
        
        let face_detected = !self.detections.is_empty();
        let eye_variance = self.calculate_eye_variance();
        let vector_count = self.eye_vectors.len();
        
        // Calculate score based on eye movement variance
        // Real humans have natural eye movement variance
        // Pre-recorded videos or photos have minimal variance
        let mut score: f64 = 1.0;
        
        if !face_detected {
            score -= 0.5;
        }
        
        if vector_count < 10 {
            score -= 0.3;
        }
        
        // Low variance suggests static image or pre-recorded video
        if eye_variance < 0.5 {
            score -= 0.4;
        }
        
        // Very high variance might indicate manipulation
        if eye_variance > 50.0 {
            score -= 0.2;
        }
        
        score = score.max(0.0).min(1.0);
        
        let status = if score >= THRESHOLD_CLEAR {
            "CLEAR".to_string()
        } else if score >= THRESHOLD_SUSPECT {
            "SUSPECT".to_string()
        } else {
            "ANOMALY".to_string()
        };
        
        IrisResult {
            score,
            status,
            eye_variance,
            vector_count,
            face_detected,
        }
    }

    /// Extract eye region from face detection
    pub fn extract_eye_region(&self, face: &FaceDetection) -> EyeLandmark {
        // Simplified eye region extraction
        // In production, this would use facial landmark detection
        let eye_x = face.x + face.width * 0.3;
        let eye_y = face.y + face.height * 0.4;
        
        EyeLandmark {
            x: eye_x,
            y: eye_y,
            eye_type: EyeType::Left,
        }
    }

    /// Extract both eye regions - returns left eye landmark
    pub fn extract_eye_regions(&self, face: &FaceDetection) -> EyeLandmark {
        let left_x = face.x + face.width * 0.3;
        let left_y = face.y + face.height * 0.4;
        
        EyeLandmark {
            x: left_x,
            y: left_y,
            eye_type: EyeType::Left,
        }
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

    #[test]
    fn test_face_detection_creation() {
        let face = FaceDetection::new(100.0, 200.0, 50.0, 60.0, 0.95);
        assert_eq!(face.x, 100.0);
        assert_eq!(face.y, 200.0);
        assert_eq!(face.width, 50.0);
        assert_eq!(face.height, 60.0);
        assert_eq!(face.confidence, 0.95);
    }

    #[test]
    fn test_eye_landmark_creation() {
        let landmark = EyeLandmark {
            x: 120.0,
            y: 220.0,
            eye_type: EyeType::Left,
        };
        assert_eq!(landmark.x, 120.0);
        assert_eq!(landmark.y, 220.0);
        assert_eq!(matches!(landmark.eye_type, EyeType::Left), true);
    }

    #[test]
    fn test_iris_engine_creation() {
        let engine = IrisEngine::new();
        assert_eq!(engine.get_detections().len(), 0);
    }

    #[test]
    fn test_detect_faces() {
        let mut engine = IrisEngine::new();
        let image_data = vec![0u8; 640 * 480 * 3];
        let detections = engine.detect_faces(&image_data, 640, 480);
        assert_eq!(detections.len(), 0);
    }

    #[test]
    fn test_clear() {
        let mut engine = IrisEngine::new();
        let image_data = vec![0u8; 640 * 480 * 3];
        engine.detect_faces(&image_data, 640, 480);
        engine.clear();
        assert_eq!(engine.get_detections().len(), 0);
    }

    #[test]
    fn test_extract_eye_region() {
        let engine = IrisEngine::new();
        let face = FaceDetection::new(100.0, 200.0, 50.0, 60.0, 0.95);
        let eye = engine.extract_eye_region(&face);
        assert_eq!(eye.x, 100.0 + 50.0 * 0.3);
        assert_eq!(eye.y, 200.0 + 60.0 * 0.4);
    }

    #[test]
    fn test_track_eye_vector() {
        let mut engine = IrisEngine::new();
        let left_eye = EyeLandmark {
            x: 100.0,
            y: 200.0,
            eye_type: EyeType::Left,
        };
        let right_eye = EyeLandmark {
            x: 150.0,
            y: 200.0,
            eye_type: EyeType::Right,
        };
        engine.track_eye_vector(&left_eye, &right_eye);
        let variance = engine.calculate_eye_variance();
        assert_eq!(variance, 0.0); // Single vector has no variance
    }

    #[test]
    fn test_calculate_eye_variance_multiple() {
        let mut engine = IrisEngine::new();
        let left_eye1 = EyeLandmark {
            x: 100.0,
            y: 200.0,
            eye_type: EyeType::Left,
        };
        let right_eye1 = EyeLandmark {
            x: 150.0,
            y: 200.0,
            eye_type: EyeType::Right,
        };
        let left_eye2 = EyeLandmark {
            x: 105.0,
            y: 205.0,
            eye_type: EyeType::Left,
        };
        let right_eye2 = EyeLandmark {
            x: 155.0,
            y: 205.0,
            eye_type: EyeType::Right,
        };
        engine.track_eye_vector(&left_eye1, &right_eye1);
        engine.track_eye_vector(&left_eye2, &right_eye2);
        let variance = engine.calculate_eye_variance();
        assert!(variance >= 0.0);
    }

    #[test]
    fn test_analyze_insufficient_data() {
        let engine = IrisEngine::new();
        let result = engine.analyze();
        assert_eq!(result.status, "ANOMALY");
        assert_eq!(result.face_detected, false);
        assert_eq!(result.vector_count, 0);
    }

    #[test]
    fn test_analyze_with_vectors() {
        let mut engine = IrisEngine::new();
        for i in 0..20 {
            let left_eye = EyeLandmark {
                x: 100.0 + i as f32 * 0.1,
                y: 200.0,
                eye_type: EyeType::Left,
            };
            let right_eye = EyeLandmark {
                x: 150.0 + i as f32 * 0.1,
                y: 200.0,
                eye_type: EyeType::Right,
            };
            engine.track_eye_vector(&left_eye, &right_eye);
        }
        let result = engine.analyze();
        assert!(result.score >= 0.0 && result.score <= 1.0);
        assert_eq!(result.vector_count, 20);
    }

    #[test]
    fn test_eye_vector_capacity() {
        let mut engine = IrisEngine::new();
        let left_eye = EyeLandmark {
            x: 100.0,
            y: 200.0,
            eye_type: EyeType::Left,
        };
        let right_eye = EyeLandmark {
            x: 150.0,
            y: 200.0,
            eye_type: EyeType::Right,
        };
        
        // Add 105 vectors (exceeds capacity of 100)
        for _ in 0..105 {
            engine.track_eye_vector(&left_eye, &right_eye);
        }
        
        let result = engine.analyze();
        // Should only keep last 100
        assert_eq!(result.vector_count, 100);
    }
}
