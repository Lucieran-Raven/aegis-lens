/**
 * ECHO - JavaScript Integration
 * Acoustic time-of-flight measurement and analysis for interview sessions
 */

import init, { EchoEngine } from '../pkg/echo.js';

let engine = null;
let isInitialized = false;

/**
 * Initialize ECHO engine
 * @returns {Promise<void>}
 */
export async function initEcho() {
  if (isInitialized) {
    return;
  }

  try {
    await init();
    engine = new EchoEngine();
    isInitialized = true;
    console.log('ECHO engine initialized successfully');
  } catch (error) {
    console.error('Failed to initialize ECHO engine:', error);
    throw error;
  }
}

/**
 * Measure a single time-of-flight sample
 * @returns {number} TOF value in milliseconds
 */
export function measureToF() {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
  }

  return engine.measure();
}

/**
 * Perform full analysis and return result
 * @returns {Object} Analysis result with score, status, and metrics
 */
export function analyze() {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
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
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
  }

  return engine.sample_count();
}

/**
 * Clear all samples
 */
export function clearSamples() {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
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
  window.Echo = {
    init: initEcho,
    measure: measureToF,
    analyze: analyze,
    getSampleCount,
    clearSamples,
    isReady,
    getStatus
  };
}
