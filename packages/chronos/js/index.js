/**
 * CHRONOS - JavaScript Integration
 * Jitter measurement and anomaly detection for interview sessions
 */

import init, { ChronosEngine } from '../pkg/chronos.js';

let engine = null;
let isInitialized = false;

/**
 * Initialize CHRONOS engine
 * @returns {Promise<void>}
 */
export async function initChronos() {
  if (isInitialized) {
    return;
  }

  try {
    await init();
    engine = new ChronosEngine();
    isInitialized = true;
    console.log('CHRONOS engine initialized successfully');
  } catch (error) {
    console.error('Failed to initialize CHRONOS engine:', error);
    throw error;
  }
}

/**
 * Measure a single timing sample
 * @returns {number} Jitter value in milliseconds
 */
export function measureJitter() {
  if (!isInitialized || !engine) {
    throw new Error('CHRONOS engine not initialized. Call initChronos() first.');
  }

  return engine.measure();
}

/**
 * Perform full analysis and return result
 * @returns {Object} Analysis result with score, status, and metrics
 */
export function analyze() {
  if (!isInitialized || !engine) {
    throw new Error('CHRONOS engine not initialized. Call initChronos() first.');
  }

  const result = engine.analyze();
  return JSON.parse(result);
}

/**
 * Get current sample count
 * @returns {number} Number of samples collected
 */
export function getSampleCount() {
  if (!isInitialized || !engine) {
    throw new Error('CHRONOS engine not initialized. Call initChronos() first.');
  }

  return engine.sample_count();
}

/**
 * Clear all samples
 */
export function clearSamples() {
  if (!isInitialized || !engine) {
    throw new Error('CHRONOS engine not initialized. Call initChronos() first.');
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
    sampleCount: isInitialized ? getSampleCount() : 0,
    windowSize: 1000
  };
}

// Export for window object (for browser usage)
if (typeof window !== 'undefined') {
  window.Chronos = {
    init: initChronos,
    measure: measureJitter,
    analyze: analyze,
    getSampleCount,
    clearSamples,
    isReady,
    getStatus
  };
}
