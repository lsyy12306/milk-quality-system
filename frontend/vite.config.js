import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 说明：
// - build.emptyOutDir=false 是为了避开本机安全删除机制对 vite 清空 dist 的拦截（否则 build 会失败）。
// - server.proxy 把 /api 代理到后端 8000，开发期无需处理跨域。
export default defineConfig({
  plugins: [react()],
  build: { emptyOutDir: false },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
