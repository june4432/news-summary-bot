import requests
import time
import os
import subprocess
import logging
from dotenv import load_dotenv
load_dotenv()

# ✅ 로그 설정 (시간 포함)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # .env 또는 환경변수에 저장

def restart_ngrok():
    logging.info("🔁 ngrok pm2 프로세스 재시작 중...")
    # 'newsbot-ngrok' 이름이 정확하므로 그대로 사용합니다.
    res = subprocess.run(["/usr/bin/pm2", "restart", "newsbot-ngrok"], capture_output=True, text=True)
    print("stdout:", res.stdout)
    print("stderr:", res.stderr)
    # 여기를 넉넉하게 10초 또는 15초로 늘려보세요.
    time.sleep(4) # <-- 이 부분을 수정하세요!

def get_ngrok_url():
    try:
        r = requests.get("http://localhost:4040/api/tunnels")
        tunnels = r.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                logging.info(f"🌍 ngrok 주소: {tunnel['public_url']}")
                return tunnel["public_url"]
    except Exception as e:
        logging.error(f"❌ ngrok 주소 확인 실패: {e}")
    return None

def set_webhook(url):
    webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_param = f"{url}/webhook"

    logging.info("🧪 요청 형식(GET처럼 보이게):")
    logging.info(f"{webhook_url}?url={webhook_param}")

    res = requests.post(webhook_url, data={"url": webhook_param})
    logging.info(f"📬 Webhook 등록 결과: {res.json()}")

if __name__ == "__main__":
    restart_ngrok()
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        set_webhook(ngrok_url)
    else:
        logging.error("🚫 Webhook 등록 실패: ngrok URL을 찾지 못함")