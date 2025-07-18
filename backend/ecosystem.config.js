module.exports = {
  apps : [{
    name   : "newsbot-backend-app",
    script : "gunicorn",
    args   : "-w 4 -b 0.0.0.0:3200 server:app --log-level debug",
    cwd    : "/home/pi/project/news-summary-bot/backend",
    interpreter : "/home/pi/project/news-summary-bot/backend/venv/bin/python3", // 👈 'which python3' 결과와 단 한 글자도 틀림없이 붙여넣으세요!
    env_production: {
       NODE_ENV: "production",
       FLASK_ENV: "production"
    }
  }]
};