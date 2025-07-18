import json
from config import telegram_bot_token
from telegram import send_telegram_message  # 네가 위에 정의한 함수

BOT_TOKEN = telegram_bot_token  # 🔑 너의 실제 봇 토큰으로 교체
RECIPIENTS_FILE = "recipients_telegram.json"

def load_telegram_recipients():
    with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def send_test_message_to_all():
    recipients = load_telegram_recipients()

    message = (
        "🧪 *신규 기능 안내*\n\n"
        "⬇️ 메뉴의 *뉴스레터 설정하기*를 누르면\n"
        "*수신 시간대*와 *카테고리*를 선택할 수 있어요\\!\n"
        "나의 취향에 맞춰 뉴스를 받아볼 수 있습니다\\."
    )

    for person in recipients:
        chat_id = person.get("chat_id")
        subscribed = person.get("subscribed", True)
        if chat_id and subscribed:
            print(f"📨 {chat_id}에게 테스트 전송 중...")
            send_telegram_message(text=message, bot_token=BOT_TOKEN, chat_id=chat_id)

if __name__ == "__main__":
    send_test_message_to_all()