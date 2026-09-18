import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import oxlinPlugin from 'vite-plugin-oxlint';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), oxlinPlugin()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.js"
  },
})
