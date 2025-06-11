import requests
import json

RECIPIENTS_FILE = "recipients_telegram.json"

def send_telegram_message(text, bot_token, chat_id):
    print(text)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2"  # 꼭 지정해야 함!
    }
    response = requests.post(url, data=payload)
    if not response.ok:
        print("❌ 텔레그램 전송 실패:", response.text)


def load_recipients():
    try:
        with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_recipients(data):
    with open(RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)