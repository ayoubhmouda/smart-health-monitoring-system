import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    host: '0.0.0.0',   // يسمح بالاتصالات من أي جهاز على الشبكة
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Django
        changeOrigin: true,
      }
    }
  }
})