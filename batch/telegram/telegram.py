import requests
import json
from batch.common.config import telegram_bot_token
from batch.common.log import logger

TELEGRAM_RECIPIENTS_FILE = "recipients_telegram.json"

# 뉴스 보낼 때 사용하는 텔레그램 메세지 전송 기능
def send_telegram_message(text, chat_id):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2"  # 꼭 지정해야 함!
    }
    response = requests.post(url, data=payload)
    if not response.ok:
        logger.warning(f"❌ 텔레그램 전송 실패: {response.text}")

# 텔레그램 사용자 정보 가져오기 
def load_recipients():
    try:
        with open(TELEGRAM_RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# 텔레그램 사용자 정보 저장하기
def save_recipients(data):
    with open(TELEGRAM_RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 텔레그램 봇에서 사용하는 메세지 전송 기능
def send_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {"chat_id": chat_id, 
            "text": text,
            "parse_mode": parse_mode
            }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, data=data)
    logger.info(response.json())