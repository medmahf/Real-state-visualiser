import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En dev : proxy vers le backend FastAPI (port 8000). En prod : tout est servi par FastAPI.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/communes_94.geojson': 'http://localhost:8000',
    },
  },
  build: { outDir: 'dist' },
})
