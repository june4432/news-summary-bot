import json
from mailer import send_email, get_email_subject, build_email_body
from config import sender_email, sender_app_password, notion_url


def load_recipients(filepath="recipients.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def send_bulk_email(news_data):
    recipients = load_recipients()
    subject = get_email_subject()

    for person in recipients:
        name = person.get("name", "수신자")
        email = person["email"]
        print(f"📬 {name} ({email})에게 메일 전송 중...")

        greeting = f"<p style='font-size: 16px;'>안녕하세요 <strong>{name}</strong>님 👋</p><br>"
        body = greeting + build_email_body(news_data, notion_url)

        send_email(sender_email, sender_app_password, email, subject, body)

    print("✅ 모든 수신자에게 메일 전송 완료")
