import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/mtg-quiz-app/' : '/',
  server: {
    host: true,
    port: 5173,
    open: false
  }
})