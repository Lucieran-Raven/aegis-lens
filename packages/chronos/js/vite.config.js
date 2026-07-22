import { defineConfig } from 'vite';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'pkg/',
        '*.test.js'
      ]
    }
  },
  build: {
    target: 'esnext',
    module: true
  }
});
