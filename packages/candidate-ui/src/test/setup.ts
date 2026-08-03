import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock MediaStream for tests
global.MediaStream = class MediaStream {
  constructor() {}
  getTracks() {
    return [];
  }
  getVideoTracks() {
    return [];
  }
  getAudioTracks() {
    return [];
  }
} as any;

// Mock navigator.mediaDevices
Object.defineProperty(global.navigator, 'mediaDevices', {
  value: {
    getUserMedia: vi.fn(() => Promise.resolve(new MediaStream())),
    getDisplayMedia: vi.fn(() => Promise.resolve(new MediaStream())),
  },
  writable: true,
});
