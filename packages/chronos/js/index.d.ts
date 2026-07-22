/**
 * CHRONOS TypeScript Definitions
 */

export interface ChronosResult {
  score: number;
  status: string;
  meanJitter: number;
  stdJitter: number;
  shapiroW: number;
  klDivergence: number;
  sampleCount: number;
}

export interface ChronosStatus {
  initialized: boolean;
  sampleCount: number;
  windowSize: number;
}

/**
 * Initialize CHRONOS engine
 */
export function initChronos(): Promise<void>;

/**
 * Measure a single timing sample
 */
export function measureJitter(): number;

/**
 * Perform full analysis and return result
 */
export function analyze(): ChronosResult;

/**
 * Get current sample count
 */
export function getSampleCount(): number;

/**
 * Clear all samples
 */
export function clearSamples(): void;

/**
 * Check if engine is initialized
 */
export function isReady(): boolean;

/**
 * Get engine status
 */
export function getStatus(): ChronosStatus;

/**
 * Window object for browser usage
 */
export interface WindowChronos {
  init: () => Promise<void>;
  measure: () => number;
  analyze: () => ChronosResult;
  getSampleCount: () => number;
  clearSamples: () => void;
  isReady: () => boolean;
  getStatus: () => ChronosStatus;
}

declare global {
  interface Window {
    Chronos?: WindowChronos;
  }
}
