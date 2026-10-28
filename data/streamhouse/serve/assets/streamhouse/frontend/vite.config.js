import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
export default defineConfig({
  plugins: [react()],
  envDir: path.resolve(__dirname, '..'),
  css: { preprocessorOptions: { scss: { includePaths: ['node_modules'], silenceDeprecations: ['if-function', 'legacy-js-api'] } } },
  resolve: {
    alias: {
      '../flink': path.resolve(__dirname, '../flink'),
      '~@ibm/plex': path.resolve(__dirname, 'node_modules/@ibm/plex'),
    },
  },
  server: { port: 5173, host: '0.0.0.0', proxy: {'/api': 'http://localhost:4000'} },
  preview: { port: 4173, proxy: {'/api': 'http://localhost:4000'} }
});
