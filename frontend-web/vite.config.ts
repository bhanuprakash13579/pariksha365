import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    headers: {
      "Cross-Origin-Opener-Policy": "same-origin-allow-popups"
    }
  },
  build: {
    // Split the vendor bundle so the heavy libs (charts, axios+react-router)
    // hash independently from app code. Without this, every app-side change
    // busts the entire vendor cache for returning users.
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'oauth': ['@react-oauth/google'],
          'http': ['axios'],
        },
      },
    },
    // Bumped slightly above the default 500KB to avoid noisy warnings on the
    // admin chunk which legitimately ships the quiz/exam manager UIs.
    chunkSizeWarningLimit: 800,
  },
})
