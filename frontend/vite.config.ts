import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // In local dev, proxy /api/* to the Render backend (mirrors Vercel rewrite in prod)
      '/api': {
        target: 'https://hr-verification.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})

