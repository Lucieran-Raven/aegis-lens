/**
 * IRIS - JavaScript Integration
 * Face detection and eye movement analysis for liveness detection
 */

import init, { IrisEngine, FaceDetection, EyeLandmark, EyeType } from '../pkg/iris.js';

let engine = null;
let isInitialized = false;

/**
 * Initialize IRIS engine
 * @returns {Promise<void>}
 */
export async function initIris() {
  if (isInitialized) {
    return;
  }

  try {
    await init();
    engine = new IrisEngine();
    isInitialized = true;
    console.log('IRIS engine initialized successfully');
  } catch (error) {
    console.error('Failed to initialize IRIS engine:', error);
    throw error;
  }
}

/**
 * Detect faces from image data
 * @param {Uint8Array} imageData - Raw image data
 * @param {number} width - Image width
 * @param {number} height - Image height
 * @returns {Array<FaceDetection>} Array of face detections
 */
export function detectFaces(imageData, width, height) {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  return engine.detect_faces(imageData, width, height);
}

/**
 * Extract eye region from face detection
 * @param {FaceDetection} face - Face detection result
 * @returns {EyeLandmark} Eye landmark
 */
export function extractEyeRegion(face) {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  return engine.extract_eye_region(face);
}

/**
 * Track eye vector movement
 * @param {EyeLandmark} leftEye - Left eye landmark
 * @param {EyeLandmark} rightEye - Right eye landmark
 */
export function trackEyeVector(leftEye, rightEye) {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  engine.track_eye_vector(leftEye, rightEye);
}

/**
 * Calculate eye movement variance
 * @returns {number} Variance value
 */
export function calculateEyeVariance() {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  return engine.calculate_eye_variance();
}

/**
 * Perform full analysis and return result
 * @returns {Object} Analysis result with score, status, and metrics
 */
export function analyze() {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  const result = engine.analyze();
  return {
    score: result.score,
    status: result.status,
    eye_variance: result.eye_variance,
    vector_count: result.vector_count,
    face_detected: result.face_detected
  };
}

/**
 * Get current face detections
 * @returns {Array<FaceDetection>} Array of face detections
 */
export function getDetections() {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  return engine.get_detections();
}

/**
 * Clear all detections and vectors
 */
export function clear() {
  if (!isInitialized || !engine) {
    throw new Error('IRIS engine not initialized. Call initIris() first.');
  }

  engine.clear();
}

/**
 * Check if engine is initialized
 * @returns {boolean}
 */
export function isReady() {
  return isInitialized;
}

/**
 * Get engine status
 * @returns {Object} Status information
 */
export function getStatus() {
  return {
    initialized: isInitialized,
    detectionCount: isInitialized ? getDetections().length : 0,
    vectorCapacity: 100
  };
}

// Export for window object (for browser usage)
if (typeof window !== 'undefined') {
  window.Iris = {
    init: initIris,
    detectFaces,
    extractEyeRegion,
    trackEyeVector,
    calculateEyeVariance,
    analyze,
    getDetections,
    clear,
    isReady,
    getStatus
  };
}
