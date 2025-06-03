import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import serveStatic from 'serve-static';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      // Add custom middleware to serve /attack-navigator
      configureServer(server) {
        server.middlewares.use(
          '/attack-navigator/assets/config.json',
          serveStatic(path.resolve('../navigator-config/mitre_attack_local/config/config_local.json')),
        );
        server.middlewares.use(
          '/attack-navigator/mitre_attack_local',
          serveStatic(path.resolve('../navigator-config/mitre_attack_local/')),
        );
        server.middlewares.use(
          '/attack-navigator',
          serveStatic(path.resolve('../attack-navigator/nav-app/dist'), {
            index: ['index.html'],
          }),
        );
      },
    },
  ],
  build: {
    outDir: './dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
