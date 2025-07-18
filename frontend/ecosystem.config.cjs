module.exports = {
  apps : [{
    name: "newsbot-frontend-app", // PM2에서 앱을 식별할 이름
    script: "npm",           // 실행할 명령어
    args: "run dev -- --host=0.0.0.0", // npm run dev 명령과 옵션
    cwd: "/home/pi/project/news-summary-bot/frontend", // ⚠️ 여기에 실제 프로젝트 경로를 입력하세요 (예: /home/pi/project/news-summary-bot-divide/frontend)
    interpreter: "/home/pi/.nvm/versions/node/v20.19.4/bin/node", // Node.js 인터프리터 경로 (대부분 이 경로)
    watch: true,             // 파일 변경 감지 시 자동 재시작 (개발 모드에서 유용)
    ignore_watch: ["node_modules", "logs", "*.log"], // 감시에서 제외할 디렉토리/파일
    env: {
      NODE_ENV: "development", // 개발 환경으로 설정
    },
    // max_memory_restart: "1G", // 메모리 사용량 제한 (선택 사항)
  }]
};
