import requests
import time
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # .env 또는 환경변수에 저장

def restart_ngrok():
    print("🔁 ngrok pm2 프로세스 재시작 중...")
    subprocess.run(["pm2", "restart", "ngrok-newsbot"])
    time.sleep(3)  # 안정적 대기

def get_ngrok_url():
    try:
        r = requests.get("http://localhost:4040/api/tunnels")
        tunnels = r.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                print(f"🌍 ngrok 주소: {tunnel['public_url']}")
                return tunnel["public_url"]
    except Exception as e:
        print("❌ ngrok 주소 확인 실패:", e)
    return None

def set_webhook(url):
    webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_param = f"{url}/webhook"

    # 시각적 확인용 전체 URL처럼 출력 (실제 호출은 POST!)
    print("🧪 요청 형식(GET처럼 보이게):")
    print(f"{webhook_url}?url={webhook_param}")

    res = requests.post(webhook_url, data={"url": webhook_param})
    print("📬 Webhook 등록 결과:", res.json())

if __name__ == "__main__":
    restart_ngrok()
    ngrok_url = get_ngrok_url()
    print(ngrok_url)
    if ngrok_url:
        set_webhook(ngrok_url)
    else:
        print("🚫 Webhook 등록 실패: ngrok URL을 찾지 못함")