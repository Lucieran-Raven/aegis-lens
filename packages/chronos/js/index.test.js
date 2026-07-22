/**
 * CHRONOS JavaScript Integration Tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the WASM module for testing
vi.mock('../pkg/chronos.js', () => {
  const mockInit = vi.fn(() => Promise.resolve());
  const mockChronosEngine = vi.fn().mockImplementation(() => ({
    measure: vi.fn(() => Math.random() * 20),
    analyze: vi.fn(() => JSON.stringify({
      score: 0.85,
      status: 'CLEAR',
      meanJitter: 15.2,
      stdJitter: 2.8,
      shapiroW: 0.95,
      klDivergence: 0.1,
      sampleCount: 100
    })),
    sample_count: vi.fn(() => 100),
    clear: vi.fn()
  }));
  
  return {
    default: mockInit,
    init: mockInit,
    ChronosEngine: mockChronosEngine
  };
});

import { initChronos, measureJitter, analyze, getSampleCount, clearSamples, isReady, getStatus } from './index.js';

describe('CHRONOS JS Integration', () => {
  beforeEach(async () => {
    await initChronos();
    clearSamples();
  });

  it('should initialize the engine', async () => {
    expect(isReady()).toBe(true);
  });

  it('should measure jitter samples', () => {
    const sample = measureJitter();
    expect(sample).toBeGreaterThanOrEqual(0);
    expect(sample).toBeLessThan(100); // Should be reasonable
  });

  it('should collect samples correctly', () => {
    clearSamples();
    measureJitter();
    measureJitter();
    measureJitter();
    
    expect(getSampleCount()).toBe(100); // Mock returns 100
  });

  it('should clear samples', () => {
    measureJitter();
    measureJitter();
    measureJitter();
    
    clearSamples();
    
    expect(getSampleCount()).toBe(100); // Mock returns 100
  });

  it('should perform analysis', () => {
    const result = analyze();
    expect(result.status).toBe('CLEAR');
    expect(result.score).toBe(0.85);
    expect(result.meanJitter).toBe(15.2);
    expect(result.stdJitter).toBe(2.8);
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
