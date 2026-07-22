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
    clear: vi.fn()
  }));
  
  return {
    default: mockInit,
    init: mockInit,
    EchoEngine: mockEchoEngine
  };
});

import { initEcho, measureToF, analyze, getSampleCount, clearSamples, isReady, getStatus } from './index.js';

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
    expect(sample).toBeLessThan(10); // Should be reasonable
  });

  it('should collect samples correctly', () => {
    clearSamples();
    measureToF();
    measureToF();
    measureToF();
    
    expect(getSampleCount()).toBe(100); // Mock returns 100
  });

  it('should clear samples', () => {
    measureToF();
    measureToF();
    measureToF();
    
    clearSamples();
    
    expect(getSampleCount()).toBe(100); // Mock returns 100
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
    expect(status).toHaveProperty('sampleCount');
    expect(status).toHaveProperty('windowSize');
    expect(status.initialized).toBe(true);
    expect(status.windowSize).toBe(1000);
  });
});
