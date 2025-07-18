import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/news-bot/', // 👈 이 설정이 가장 중요합니다.
  server: {
    host: true,
    allowedHosts: ['june4432.ipdisk.co.kr', 'leeyoungjun.duckdns.org'],
    port: 5173,
  },
});