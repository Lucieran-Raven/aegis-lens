/**
 * ECHO - JavaScript Integration
 * Acoustic time-of-flight measurement and analysis for interview sessions
 */

import init, { EchoEngine } from '../pkg/echo.js';

let engine = null;
let isInitialized = false;
let audioContext = null;
let isAudioInitialized = false;

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
 * Initialize Web Audio API
 * @returns {Promise<AudioContext>}
 */
export async function initAudio() {
  if (isAudioInitialized && audioContext) {
    return audioContext;
  }

  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioContext = new AudioContextClass();
    isAudioInitialized = true;
    console.log('Web Audio API initialized successfully');
    return audioContext;
  } catch (error) {
    console.error('Failed to initialize Web Audio API:', error);
    throw error;
  }
}

/**
 * Generate a chirp signal
 * @param {Object} config - Chirp configuration
 * @param {number} config.startFrequency - Start frequency in Hz
 * @param {number} config.endFrequency - End frequency in Hz
 * @param {number} config.duration - Duration in seconds
 * @param {number} config.sampleRate - Sample rate in Hz
 * @returns {Object} Chirp signal with samples and config
 */
export function generateChirp(config = {}) {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
  }

  const defaultConfig = {
    startFrequency: 1000.0,
    endFrequency: 8000.0,
    duration: 0.1,
    sampleRate: 44100.0,
    ...config
  };

  const chirp = engine.generate_chirp(
    defaultConfig.startFrequency,
    defaultConfig.endFrequency,
    defaultConfig.duration,
    defaultConfig.sampleRate
  );

  return JSON.parse(chirp);
}

/**
 * Generate a chirp signal with default configuration
 * @returns {Object} Chirp signal with samples and config
 */
export function generateChirpDefault() {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
  }

  const chirp = engine.generate_chirp_default();
  return JSON.parse(chirp);
}

/**
 * Play a chirp signal through Web Audio API
 * @param {Object} chirp - Chirp signal object from generateChirp
 * @returns {Promise<AudioBufferSourceNode>} Audio source node
 */
export async function playChirp(chirp) {
  if (!isAudioInitialized || !audioContext) {
    await initAudio();
  }

  const { samples, config } = chirp;
  const audioBuffer = audioContext.createBuffer(1, samples.length, config.sampleRate);
  const channelData = audioBuffer.getChannelData(0);

  for (let i = 0; i < samples.length; i++) {
    channelData[i] = samples[i];
  }

  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);
  source.start();

  return source;
}

/**
 * Measure time-of-flight using audio chirp
 * @param {Object} chirp - Chirp signal object
 * @returns {Promise<number>} Time-of-flight in milliseconds
 */
export async function measureAudioToF(chirp) {
  if (!isAudioInitialized || !audioContext) {
    await initAudio();
  }

  const startTime = performance.now();

  // Play chirp
  await playChirp(chirp);

  const endTime = performance.now();
  const tof = endTime - startTime;

  // Store in engine
  if (isInitialized && engine) {
    engine.measure();
  }

  return tof;
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
 * Check if audio is initialized
 * @returns {boolean}
 */
export function isAudioReady() {
  return isAudioInitialized;
}

/**
 * Perform FFT-based cross-correlation between two signals
 * @param {Float32Array} signal1 - First signal
 * @param {Float32Array} signal2 - Second signal
 * @returns {Float32Array} Cross-correlation result
 */
export function crossCorrelationFFT(signal1, signal2) {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
  }

  const correlation = engine.cross_correlation_fft(signal1, signal2);
  return new Float32Array(correlation);
}

/**
 * Find the lag with maximum correlation
 * @param {Float32Array} correlation - Cross-correlation result
 * @returns {Object} Object with lag and value properties
 */
export function findPeakLag(correlation) {
  if (!isInitialized || !engine) {
    throw new Error('ECHO engine not initialized. Call initEcho() first.');
  }

  const result = engine.find_peak_lag(correlation);
  return JSON.parse(result);
}

/**
 * Get engine status
 * @returns {Object} Status information
 */
export function getStatus() {
  return {
    initialized: isInitialized,
    audioInitialized: isAudioInitialized,
    sampleCount: isInitialized ? getSampleCount() : 0,
    windowSize: 1000
  };
}

// Export for window object (for browser usage)
if (typeof window !== 'undefined') {
  window.Echo = {
    init: initEcho,
    initAudio,
    generateChirp,
    generateChirpDefault,
    playChirp,
    measureAudioToF,
    measure: measureToF,
    analyze,
    getSampleCount,
    clearSamples,
    isReady,
    isAudioReady,
    crossCorrelationFFT,
    findPeakLag,
    getStatus
  };
}
