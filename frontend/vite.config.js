import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load env variables from project root
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');

  return {
    plugins: [react()],
    define: {
      // Make the root env variable accessible to frontend
      'import.meta.env.VITE_PAGE_PASSWORD': JSON.stringify(env.VITE_PAGE_PASSWORD),
    },
  };
});
