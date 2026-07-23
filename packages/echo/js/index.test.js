/**
 * ECHO JavaScript Integration Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the WASM module for testing
vi.mock('../pkg/echo.js', () => {
  const mockInit = vi.fn(() => Promise.resolve());
  const mockEchoEngine = vi.fn().mockImplementation(() => ({
    measure: vi.fn(() => Math.random() * 2),
    analyze: vi.fn(() => JSON.stringify({
      score: 0.85,
      status: 'CLEAR',
      meanTof: 0.5,
      stdTof: 0.1,
      spectralCentroid: 0.5,
      zeroCrossingRate: 0.1,
      sampleCount: 100
    })),
    sample_count: vi.fn(() => 100),
    clear: vi.fn(),
    generate_chirp: vi.fn((startFreq, endFreq, duration, sampleRate) => JSON.stringify({
      samples: Array(4410).fill(0).map((_, i) => Math.sin(i * 0.1)),
      config: {
        startFrequency: startFreq,
        endFrequency: endFreq,
        duration: duration,
        sampleRate: sampleRate
      }
    })),
    generate_chirp_default: vi.fn(() => JSON.stringify({
      samples: Array(4410).fill(0).map((_, i) => Math.sin(i * 0.1)),
      config: {
        startFrequency: 1000.0,
        endFrequency: 8000.0,
        duration: 0.1,
        sampleRate: 44100.0
      }
    })),
    cross_correlation_fft: vi.fn((signal1, signal2) => {
      const n = signal1.length + signal2.length - 1;
      return new Float32Array(n).fill(0).map((_, i) => i === 0 ? 1.0 : 0.0);
    }),
    find_peak_lag: vi.fn((correlation) => JSON.stringify({
      lag: 0,
      value: 1.0
    }))
  }));

  return {
    default: mockInit,
    init: mockInit,
    EchoEngine: mockEchoEngine
  };
});

import {
  initEcho,
  initAudio,
  generateChirp,
  generateChirpDefault,
  playChirp,
  measureAudioToF,
  measureToF,
  analyze,
  getSampleCount,
  clearSamples,
  isReady,
  isAudioReady,
  crossCorrelationFFT,
  findPeakLag,
  getStatus
} from './index.js';

describe('ECHO JS Integration', () => {
  beforeEach(async () => {
    await initEcho();
    clearSamples();
  });

  it('should initialize the engine', async () => {
    expect(isReady()).toBe(true);
  });

  it('should measure TOF samples', () => {
    const sample = measureToF();
    expect(sample).toBeGreaterThanOrEqual(0);
    expect(sample).toBeLessThan(10);
  });

  it('should collect samples correctly', () => {
    clearSamples();
    measureToF();
    measureToF();
    measureToF();

    expect(getSampleCount()).toBe(100);
  });

  it('should clear samples', () => {
    measureToF();
    measureToF();
    measureToF();

    clearSamples();

    expect(getSampleCount()).toBe(100);
  });

  it('should perform analysis', () => {
    const result = analyze();
    expect(result.status).toBe('CLEAR');
    expect(result.score).toBe(0.85);
    expect(result.meanTof).toBe(0.5);
    expect(result.stdTof).toBe(0.1);
    expect(result.sampleCount).toBe(100);
  });

  it('should return engine status', () => {
    const status = getStatus();
    expect(status).toHaveProperty('initialized');
    expect(status).toHaveProperty('audioInitialized');
    expect(status).toHaveProperty('sampleCount');
    expect(status).toHaveProperty('windowSize');
    expect(status.initialized).toBe(true);
    expect(status.windowSize).toBe(1000);
  });

  it('should generate chirp with custom config', () => {
    const chirp = generateChirp({
      startFrequency: 500.0,
      endFrequency: 2000.0,
      duration: 0.05,
      sampleRate: 22050.0
    });
    expect(chirp).toHaveProperty('samples');
    expect(chirp).toHaveProperty('config');
    expect(chirp.config.startFrequency).toBe(500.0);
    expect(chirp.config.endFrequency).toBe(2000.0);
    expect(chirp.config.duration).toBe(0.05);
    expect(chirp.config.sampleRate).toBe(22050.0);
  });

  it('should generate chirp with default config', () => {
    const chirp = generateChirpDefault();
    expect(chirp).toHaveProperty('samples');
    expect(chirp).toHaveProperty('config');
    expect(chirp.config.startFrequency).toBe(1000.0);
    expect(chirp.config.endFrequency).toBe(8000.0);
    expect(chirp.config.duration).toBe(0.1);
    expect(chirp.config.sampleRate).toBe(44100.0);
  });

  it('should generate chirp with default parameters when no config provided', () => {
    const chirp = generateChirp();
    expect(chirp).toHaveProperty('samples');
    expect(chirp).toHaveProperty('config');
    expect(chirp.config.startFrequency).toBe(1000.0);
    expect(chirp.config.endFrequency).toBe(8000.0);
  });

  it('should check audio readiness', () => {
    expect(isAudioReady()).toBe(false);
  });

  it('should perform FFT cross-correlation', () => {
    const signal1 = new Float32Array([1.0, 2.0, 3.0]);
    const signal2 = new Float32Array([1.0, 2.0, 3.0]);
    const correlation = crossCorrelationFFT(signal1, signal2);

    expect(correlation).toBeInstanceOf(Float32Array);
    expect(correlation.length).toBe(signal1.length + signal2.length - 1);
  });

  it('should find peak lag in correlation', () => {
    const correlation = new Float32Array([1.0, 5.0, 3.0, 2.0]);
    const peak = findPeakLag(correlation);

    expect(peak).toHaveProperty('lag');
    expect(peak).toHaveProperty('value');
    expect(typeof peak.lag).toBe('number');
    expect(typeof peak.value).toBe('number');
  });
});
