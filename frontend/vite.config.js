import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// En dev : proxy vers le backend FastAPI (port 8000). En prod : tout est servi par FastAPI.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/communes_94.geojson': 'http://localhost:8000',
    },
  },
  build: { outDir: 'dist' },
})
