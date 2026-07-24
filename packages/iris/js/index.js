/**
 * IRIS - JavaScript Integration with MediaPipe
 * Face detection and eye movement analysis for liveness detection
 */

import init, { IrisEngine, FaceDetection, EyeLandmark, EyeType } from '../pkg/iris.js';
import { FaceMesh } from '@mediapipe/face_mesh';
import { Camera } from '@mediapipe/camera_utils';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';

let engine = null;
let isInitialized = false;
let faceMesh = null;
let camera = null;
let videoElement = null;
let isRunning = false;
let onResultCallback = null;
let onErrorCallback = null;

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
 * Initialize IRIS with MediaPipe FaceMesh
 * @param {HTMLVideoElement} video - Video element for camera input
 * @param {Object} options - Configuration options
 * @returns {Promise<Object>} IrisClient instance
 */
export async function initializeWithMediaPipe(video, options = {}) {
  videoElement = video;
  
  // Initialize WASM engine
  await initIris();
  
  // Initialize MediaPipe Face Mesh
  faceMesh = new FaceMesh({
    locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
    }
  });
  
  faceMesh.setOptions({
    maxNumFaces: options.maxNumFaces || 1,
    refineLandmarks: options.refineLandmarks !== false,
    minDetectionConfidence: options.minDetectionConfidence || 0.5,
    minTrackingConfidence: options.minTrackingConfidence || 0.5
  });
  
  faceMesh.onResults((results) => {
    handleFaceResults(results);
  });
  
  // Initialize camera
  camera = new Camera(video, {
    onFrame: async () => {
      await faceMesh.send({ image: video });
    },
    width: options.width || 640,
    height: options.height || 480
  });
  
  console.log('IRIS with MediaPipe initialized successfully');
  return irisClient;
}

/**
 * Handle face detection results from MediaPipe
 * @param {Object} results - MediaPipe FaceMesh results
 */
function handleFaceResults(results) {
  if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
    // No face detected
    if (onResultCallback) {
      onResultCallback({
        status: 'NO_FACE',
        score: 0.0,
        smoothness: 0.0,
        consistency: 0.0,
        entropy: 0.0,
        message: 'No face detected'
      });
    }
    return;
  }
  
  const landmarks = results.multiFaceLandmarks[0];
  
  // MediaPipe Face Mesh landmark indices for eyes
  // Left eye: 33, 133, 157, 158, 159, 160, 161, 173, 246
  // Right eye: 362, 263, 387, 386, 385, 384, 398, 466
  
  const leftEyeIndices = [33, 133, 157, 158, 159, 160, 161, 173, 246];
  const rightEyeIndices = [362, 263, 387, 386, 385, 384, 398, 466];
  
  // Get left eye points
  const leftPoints = leftEyeIndices.map(idx => ({
    x: landmarks[idx].x,
    y: landmarks[idx].y
  }));
  
  // Get right eye points
  const rightPoints = rightEyeIndices.map(idx => ({
    x: landmarks[idx].x,
    y: landmarks[idx].y
  }));
  
  // Calculate pupil position (center of eye)
  const leftPupil = {
    x: leftPoints.reduce((sum, p) => sum + p.x, 0) / leftPoints.length,
    y: leftPoints.reduce((sum, p) => sum + p.y, 0) / leftPoints.length
  };
  
  const rightPupil = {
    x: rightPoints.reduce((sum, p) => sum + p.x, 0) / rightPoints.length,
    y: rightPoints.reduce((sum, p) => sum + p.y, 0) / rightPoints.length
  };
  
  // Detect glints (simplified - use corner of eye as proxy)
  // In production, you'd use image analysis to find actual glints
  const leftGlint = {
    x: leftPoints[0].x + 0.02,
    y: leftPoints[0].y - 0.02
  };
  
  const rightGlint = {
    x: rightPoints[0].x + 0.02,
    y: rightPoints[0].y - 0.02
  };
  
  // Build face landmarks object for Rust
  const faceData = {
    left_eye: {
      pupil: { x: leftPupil.x, y: leftPupil.y },
      glints: [{ x: leftGlint.x, y: leftGlint.y }],
      corners: []
    },
    right_eye: {
      pupil: { x: rightPupil.x, y: rightPupil.y },
      glints: [{ x: rightGlint.x, y: rightGlint.y }],
      corners: []
    },
    nose_tip: { x: landmarks[1].x, y: landmarks[1].y },
    mouth_center: { x: landmarks[13].x, y: landmarks[13].y },
    face_bbox: {
      x: 0,
      y: 0,
      width: 1,
      height: 1
    }
  };
  
  // Process through Rust engine
  const result = engine.process_landmarks(faceData);
  
  if (onResultCallback) {
    onResultCallback({
      status: result.status,
      score: result.score,
      smoothness: result.smoothness,
      consistency: result.consistency,
      entropy: result.trajectory_entropy,
      left_vector: result.left_vector,
      right_vector: result.right_vector,
      sample_count: result.sample_count,
      message: `Face detected: ${result.status}`
    });
  }
}

/**
 * Start camera and face detection
 * @returns {Promise<void>}
 */
export async function startCamera() {
  if (!camera) {
    throw new Error('Camera not initialized. Call initializeWithMediaPipe() first.');
  }
  await camera.start();
  isRunning = true;
  console.log('IRIS camera started');
}

/**
 * Stop camera and face detection
 * @returns {Promise<void>}
 */
export async function stopCamera() {
  if (camera) {
    await camera.stop();
  }
  isRunning = false;
  console.log('IRIS camera stopped');
}

/**
 * Detect faces from image data (legacy method without MediaPipe)
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
    face_detected: result.face_detected,
    smoothness: result.smoothness,
    consistency: result.consistency,
    trajectory_entropy: result.trajectory_entropy,
    left_vector: result.left_vector,
    right_vector: result.right_vector,
    sample_count: result.sample_count
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
  if (!isInitialized || !engine) {
    return { status: 'NOT_INITIALIZED' };
  }
  const result = engine.analyze();
  return {
    status: result.status,
    score: result.score,
    sample_count: result.sample_count,
    smoothness: result.smoothness,
    consistency: result.consistency,
    trajectory_entropy: result.trajectory_entropy
  };
}

/**
 * Set result callback
 * @param {Function} callback - Callback function for results
 */
export function onResult(callback) {
  onResultCallback = callback;
}

/**
 * Set error callback
 * @param {Function} callback - Callback function for errors
 */
export function onError(callback) {
  onErrorCallback = callback;
}

/**
 * Iris client object for chaining
 */
const irisClient = {
  initialize: initializeWithMediaPipe,
  start: startCamera,
  stop: stopCamera,
  analyze,
  clear,
  getStatus,
  onResult,
  onError
};

// Export for window object (for browser usage)
if (typeof window !== 'undefined') {
  window.Iris = {
    init: initIris,
    initializeWithMediaPipe,
    detectFaces,
    extractEyeRegion,
    trackEyeVector,
    calculateEyeVariance,
    analyze,
    getDetections,
    clear,
    isReady,
    getStatus,
    startCamera,
    stopCamera,
    onResult,
    onError
  };
}
