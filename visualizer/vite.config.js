import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

const artifactsDirectory = fileURLToPath(new URL('../artifacts', import.meta.url));

export default defineConfig({
  base: './',
  publicDir: artifactsDirectory,
  build: {
    emptyOutDir: true,
    outDir: 'dist',
  },
});
