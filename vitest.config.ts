import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    // Test files location
    include: ['tests/frontend/**/*.test.ts'],

    // Environment
    environment: 'node',

    // Coverage settings
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['frontend/utils/**/*.ts'],
      exclude: ['**/node_modules/**', '**/*.d.ts'],
    },

    // Resolve aliases to match the project structure


    // Global settings
    globals: true,
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, './frontend'),
    },
  },
});
