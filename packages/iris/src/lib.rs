//! Iris - Computer vision and facial analysis
//!
//! This module provides utilities for computer vision, facial recognition,
//! and image processing operations.

use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
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

/// Face landmarks (simple version for basic detection)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimpleFaceLandmarks {
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
    pub smoothness: f32,
    pub consistency: f32,
    pub trajectory_entropy: f32,
    pub left_vector: Point2D,
    pub right_vector: Point2D,
    pub sample_count: usize,
}

/// Frame processing result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen(getter_with_clone)]
pub struct FrameResult {
    pub status: String,
    pub left_eye: Option<EyeLandmark>,
    pub right_eye: Option<EyeLandmark>,
    pub face_detected: bool,
}

/// 2D Point
#[derive(Debug, Clone, Serialize, Deserialize)]
#[wasm_bindgen]
pub struct Point2D {
    pub x: f32,
    pub y: f32,
}

/// Bounding box
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BoundingBox {
    pub x: f32,
    pub y: f32,
    pub width: f32,
    pub height: f32,
}

/// Eye landmarks with pupil and glints
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EyeLandmarks {
    pub pupil: Point2D,
    pub glints: Vec<Point2D>,
    pub corners: Vec<Point2D>,
}

/// Face landmarks from MediaPipe
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaPipeFaceLandmarks {
    pub left_eye: EyeLandmarks,
    pub right_eye: EyeLandmarks,
    pub nose_tip: Point2D,
    pub mouth_center: Point2D,
    pub face_bbox: BoundingBox,
}

/// Eye data for trajectory tracking
#[derive(Debug, Clone)]
struct EyeData {
    #[allow(dead_code)]
    pupil_x: f32,
    #[allow(dead_code)]
    pupil_y: f32,
    #[allow(dead_code)]
    glint_x: f32,
    #[allow(dead_code)]
    glint_y: f32,
    vector_x: f32,
    vector_y: f32,
}

/// Attack type enum
#[derive(Debug, Clone, PartialEq)]
enum AttackType {
    None,
    StaticPhoto,
    AIAvatar,
    Deepfake,
    VirtualWebcam,
    ProxyCandidate,
}

/// IRIS engine for face detection and analysis
#[wasm_bindgen]
pub struct IrisEngine {
    detections: Vec<FaceDetection>,
    eye_vectors: Vec<(f32, f32)>,
    trajectory_left: VecDeque<EyeData>,
    trajectory_right: VecDeque<EyeData>,
    window_size: usize,
}

impl Default for IrisEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[wasm_bindgen]
impl IrisEngine {
    /// Create new IRIS engine
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self {
            detections: Vec::new(),
            eye_vectors: Vec::new(),
            trajectory_left: VecDeque::with_capacity(100),
            trajectory_right: VecDeque::with_capacity(100),
            window_size: 100,
        }
    }

    /// Detect faces from image data (simplified for WASM)
    /// In production, this would integrate with MediaPipe or similar
    pub fn detect_faces(
        &mut self,
        _image_data: &[u8],
        _width: u32,
        _height: u32,
    ) -> Vec<FaceDetection> {
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
        self.trajectory_left.clear();
        self.trajectory_right.clear();
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

        let mean_x: f32 =
            self.eye_vectors.iter().map(|v| v.0).sum::<f32>() / self.eye_vectors.len() as f32;
        let mean_y: f32 =
            self.eye_vectors.iter().map(|v| v.1).sum::<f32>() / self.eye_vectors.len() as f32;

        let variance_x: f32 = self
            .eye_vectors
            .iter()
            .map(|v| (v.0 - mean_x).powi(2))
            .sum::<f32>()
            / self.eye_vectors.len() as f32;

        let variance_y: f32 = self
            .eye_vectors
            .iter()
            .map(|v| (v.1 - mean_y).powi(2))
            .sum::<f32>()
            / self.eye_vectors.len() as f32;

        (variance_x + variance_y).sqrt()
    }

    /// Analyze eye movement and calculate liveness score
    pub fn analyze(&self) -> IrisResult {
        const THRESHOLD_CLEAR: f64 = 0.8;
        const THRESHOLD_SUSPECT: f64 = 0.5;

        let face_detected = !self.detections.is_empty();
        let eye_variance = self.calculate_eye_variance();
        let vector_count = self.eye_vectors.len();

        // Calculate enhanced metrics if trajectory data exists
        let (smoothness, consistency, entropy) = if self.trajectory_left.len() >= 2 {
            self.calculate_metrics()
        } else {
            (0.0, 0.0, eye_variance)
        };

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

        // Apply enhanced metrics penalties
        if smoothness < 0.3 {
            score -= 0.5;
        }
        if consistency < 0.4 {
            score -= 0.3;
        }
        if entropy < 0.2 {
            score -= 0.4;
        }

        score = score.clamp(0.0, 1.0);

        let status = if score >= THRESHOLD_CLEAR {
            "CLEAR".to_string()
        } else if score >= THRESHOLD_SUSPECT {
            "SUSPECT".to_string()
        } else {
            "ANOMALY".to_string()
        };

        // Get latest vectors if available
        let (left_vector, right_vector) = if let (Some(left), Some(right)) =
            (self.trajectory_left.back(), self.trajectory_right.back())
        {
            (
                Point2D {
                    x: left.vector_x,
                    y: left.vector_y,
                },
                Point2D {
                    x: right.vector_x,
                    y: right.vector_y,
                },
            )
        } else {
            (Point2D { x: 0.0, y: 0.0 }, Point2D { x: 0.0, y: 0.0 })
        };

        IrisResult {
            score,
            status,
            eye_variance,
            vector_count,
            face_detected,
            smoothness,
            consistency,
            trajectory_entropy: entropy,
            left_vector,
            right_vector,
            sample_count: self.trajectory_left.len(),
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

    /// Get sample count
    pub fn sample_count(&self) -> usize {
        self.trajectory_left.len()
    }

    /// Process a video frame and return analysis result
    /// This is a simplified implementation for testing
    /// In production, this would use MediaPipe for face detection and tracking
    pub fn process_frame(&mut self, image_data: &[u8], width: u32, height: u32) -> FrameResult {
        // Detect faces in the frame
        let detections = self.detect_faces(image_data, width, height);

        if detections.is_empty() {
            return FrameResult {
                status: "NO_FACE".to_string(),
                left_eye: None,
                right_eye: None,
                face_detected: false,
            };
        }

        // Use the first detected face
        let face = &detections[0];
        let left_eye = self.extract_eye_region(face);
        let right_eye = EyeLandmark {
            x: face.x + face.width * 0.7,
            y: face.y + face.height * 0.4,
            eye_type: EyeType::Right,
        };

        // Track eye movement
        self.track_eye_vector(&left_eye, &right_eye);

        FrameResult {
            status: "FACE_DETECTED".to_string(),
            left_eye: Some(left_eye),
            right_eye: Some(right_eye),
            face_detected: true,
        }
    }

    /// Process MediaPipe landmarks and return analysis result
    pub fn process_landmarks(&mut self, landmarks: JsValue) -> JsValue {
        let face_data: MediaPipeFaceLandmarks = serde_wasm_bindgen::from_value(landmarks)
            .unwrap_or_else(|_| MediaPipeFaceLandmarks {
                left_eye: EyeLandmarks {
                    pupil: Point2D { x: 0.0, y: 0.0 },
                    glints: vec![],
                    corners: vec![],
                },
                right_eye: EyeLandmarks {
                    pupil: Point2D { x: 0.0, y: 0.0 },
                    glints: vec![],
                    corners: vec![],
                },
                nose_tip: Point2D { x: 0.0, y: 0.0 },
                mouth_center: Point2D { x: 0.0, y: 0.0 },
                face_bbox: BoundingBox {
                    x: 0.0,
                    y: 0.0,
                    width: 1.0,
                    height: 1.0,
                },
            });

        // Extract left eye data
        let left_pupil = &face_data.left_eye.pupil;
        let left_glints = &face_data.left_eye.glints;
        let left_glint = if left_glints.is_empty() {
            Point2D { x: 0.0, y: 0.0 }
        } else {
            left_glints[0].clone()
        };

        // Calculate left eye vector
        let left_vector_x = left_glint.x - left_pupil.x;
        let left_vector_y = left_glint.y - left_pupil.y;

        // Extract right eye data
        let right_pupil = &face_data.right_eye.pupil;
        let right_glints = &face_data.right_eye.glints;
        let right_glint = if right_glints.is_empty() {
            Point2D { x: 0.0, y: 0.0 }
        } else {
            right_glints[0].clone()
        };

        let right_vector_x = right_glint.x - right_pupil.x;
        let right_vector_y = right_glint.y - right_pupil.y;

        // Store in trajectory
        self.trajectory_left.push_back(EyeData {
            pupil_x: left_pupil.x,
            pupil_y: left_pupil.y,
            glint_x: left_glint.x,
            glint_y: left_glint.y,
            vector_x: left_vector_x,
            vector_y: left_vector_y,
        });

        self.trajectory_right.push_back(EyeData {
            pupil_x: right_pupil.x,
            pupil_y: right_pupil.y,
            glint_x: right_glint.x,
            glint_y: right_glint.y,
            vector_x: right_vector_x,
            vector_y: right_vector_y,
        });

        // Maintain window size
        if self.trajectory_left.len() > self.window_size {
            self.trajectory_left.pop_front();
        }
        if self.trajectory_right.len() > self.window_size {
            self.trajectory_right.pop_front();
        }

        // Calculate metrics
        let (smoothness, consistency, entropy) = self.calculate_metrics();

        // Detect attack type
        let attack_type = self.detect_attack_type(smoothness, consistency, entropy);

        // Calculate score
        let mut score: f64 = 1.0;
        if smoothness < 0.3 {
            score -= 0.5;
        }
        if consistency < 0.4 {
            score -= 0.3;
        }
        if entropy < 0.2 {
            score -= 0.4;
        }

        // Apply attack-specific penalties
        match attack_type {
            AttackType::StaticPhoto => score -= 0.3,
            AttackType::AIAvatar => score -= 0.3,
            AttackType::Deepfake => score -= 0.4,
            AttackType::VirtualWebcam => score -= 0.3,
            AttackType::ProxyCandidate => score -= 0.2,
            AttackType::None => {}
        }

        score = score.clamp(0.0, 1.0);

        let status = if score >= 0.8 {
            "CLEAR".to_string()
        } else if score >= 0.5 {
            "SUSPECT".to_string()
        } else {
            "ANOMALY".to_string()
        };

        // Return result
        let result = IrisResult {
            score,
            status,
            eye_variance: entropy,
            vector_count: self.trajectory_left.len(),
            face_detected: true,
            smoothness,
            consistency,
            trajectory_entropy: entropy,
            left_vector: Point2D {
                x: left_vector_x,
                y: left_vector_y,
            },
            right_vector: Point2D {
                x: right_vector_x,
                y: right_vector_y,
            },
            sample_count: self.trajectory_left.len(),
        };

        serde_wasm_bindgen::to_value(&result).unwrap()
    }

    /// Calculate trajectory metrics
    fn calculate_metrics(&self) -> (f32, f32, f32) {
        if self.trajectory_left.len() < 2 {
            return (0.0, 0.0, 0.0);
        }

        // Calculate smoothness (inverse of acceleration)
        let mut smoothness = 0.0;
        let mut prev_left = &self.trajectory_left[0];
        for data in self.trajectory_left.iter().skip(1) {
            let accel = (data.vector_x - prev_left.vector_x).abs()
                + (data.vector_y - prev_left.vector_y).abs();
            smoothness += 1.0 - accel.min(1.0);
            prev_left = data;
        }
        smoothness /= self.trajectory_left.len() as f32;

        // Calculate consistency (correlation between left and right eyes)
        let mut consistency = 0.0;
        for (left, right) in self
            .trajectory_left
            .iter()
            .zip(self.trajectory_right.iter())
        {
            let left_mag = (left.vector_x.powi(2) + left.vector_y.powi(2)).sqrt();
            let right_mag = (right.vector_x.powi(2) + right.vector_y.powi(2)).sqrt();
            if left_mag > 0.0 && right_mag > 0.0 {
                let dot = left.vector_x * right.vector_x + left.vector_y * right.vector_y;
                let cos_sim = (dot / (left_mag * right_mag)).clamp(-1.0, 1.0);
                consistency += cos_sim;
            }
        }
        consistency /= self.trajectory_left.len() as f32;
        consistency = consistency.max(0.0);

        // Calculate entropy (variability in trajectory)
        let mut entropy = 0.0;
        let mut histogram = [0.0; 10];
        for data in self.trajectory_left.iter() {
            let angle = (data.vector_y.atan2(data.vector_x) + std::f32::consts::PI)
                / (2.0 * std::f32::consts::PI);
            let bin = (angle * 10.0).min(9.0) as usize;
            histogram[bin] += 1.0;
        }
        let total = self.trajectory_left.len() as f32;
        for &count in &histogram {
            if count > 0.0 {
                let p = count / total;
                entropy -= p * p.log2();
            }
        }
        entropy /= 3.32; // Normalize to 0-1 range

        (smoothness, consistency, entropy)
    }

    /// Detect attack type based on metrics
    fn detect_attack_type(&self, smoothness: f32, consistency: f32, entropy: f32) -> AttackType {
        // Check for static photo (flat trajectory)
        if entropy < 0.1 && consistency > 0.9 {
            return AttackType::StaticPhoto;
        }

        // Check for AI avatar (too smooth)
        if smoothness > 0.9 && entropy < 0.3 {
            return AttackType::AIAvatar;
        }

        // Check for deepfake (erratic glints)
        if consistency < 0.2 && smoothness < 0.3 {
            return AttackType::Deepfake;
        }

        // Check for virtual webcam (low jitter)
        if entropy < 0.2 && smoothness > 0.8 {
            return AttackType::VirtualWebcam;
        }

        // Check for proxy candidate (mismatched vectors)
        if let (Some(left), Some(right)) =
            (self.trajectory_left.back(), self.trajectory_right.back())
        {
            let vec_diff =
                (left.vector_x - right.vector_x).abs() + (left.vector_y - right.vector_y).abs();
            if vec_diff > 0.5 {
                return AttackType::ProxyCandidate;
            }
        }

        AttackType::None
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
