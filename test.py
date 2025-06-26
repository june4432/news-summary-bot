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
    "🧪 *기능 개선 도중 중복된 메세지가 여러 건 전송되었습니다\\.*\n\n"
    "알림폭탄을 보내드려 죄송합니다\\.🙏\n\n"
    "📬 *이메일로 구독하면 수신 시간대와 관심 카테고리를 자유롭게 설정할 수 있어요\\!*\n"
    "[이메일 구독하러 가기](https://leeyoungjun.duckdns.org/news-bot)"
)

    for person in recipients:
        chat_id = person.get("chat_id")
        subscribed = person.get("subscribed", True)
        if chat_id and subscribed:
            print(f"📨 {chat_id}에게 테스트 전송 중...")
            send_telegram_message(text=message, bot_token=BOT_TOKEN, chat_id=chat_id)

if __name__ == "__main__":
    send_test_message_to_all()