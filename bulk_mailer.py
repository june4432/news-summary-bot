import json
import datetime
from mailer import send_email, get_email_subject, build_email_body
from config import sender_email, sender_app_password, notion_url
from log import logger

# 경로는 상황에 맞게 조정하세요
RECIPIENTS_PATH = "/home/pi/project/news-summary-bot/recipients.json"
TOLERANCE_MINUTES = 10  # 허용 오차 범위 (분 단위)

def load_recipients(filepath=RECIPIENTS_PATH):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def get_time_key():
    now = datetime.datetime.now()
    return now.strftime("%H:%M")

def is_within_time_slot(current_time: str, slots: list[str], tolerance_minutes: int = TOLERANCE_MINUTES) -> bool:
    current_dt = datetime.datetime.strptime(current_time, "%H:%M")
    for slot in slots:
        try:
            slot_dt = datetime.datetime.strptime(slot, "%H:%M")
            diff = abs((current_dt - slot_dt).total_seconds() / 60)
            if diff <= tolerance_minutes:
                return True
        except ValueError:
            logger.warning(f"⚠️ 잘못된 시간 형식 무시됨: {slot}")
    return False

def filter_recipients_by_time_slot(recipients, current_time_key):
    return [
        r for r in recipients
        if "time_slots" in r and is_within_time_slot(current_time_key, r["time_slots"])
    ]

def send_bulk_email(news_data):
    recipients = load_recipients()
    now_key = get_time_key()
    targets = filter_recipients_by_time_slot(recipients, now_key)

    subject = get_email_subject()

    logger.info(f"⏰ 현재 시각: {now_key} 기준으로 대상자 {len(targets)}명 필터링 (±{TOLERANCE_MINUTES}분 허용)")

    for person in targets:
        name = person.get("name", "수신자")
        email = person["email"]
        logger.info(f"📬 {name} ({email})에게 메일 전송 중...")

        body = build_email_body(news_data, notion_url, email, name)
        send_email(sender_email, sender_app_password, email, subject, body)

    logger.info("✅ 전체 메일 전송 완료")