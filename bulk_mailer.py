import json
import datetime
import html2text
import time
from collections import defaultdict

from mailer import send_email, get_email_subject, build_email_body
from config import (
    sender_email, sender_app_password,
    notion_url, telegram_bot_token, telegram_chat_id
)
from log import logger
from telegram import send_telegram_message
from telegram_formatter import build_telegram_message

# 경로는 상황에 맞게 조정하세요
RECIPIENTS_PATH = "/home/pi/project/news-summary-bot/recipients_email.json"
# ✅ 텔레그램 메시지: 구독자 목록 기반 다중 전송
TELEGRAM_RECIPIENTS_PATH = "/home/pi/project/news-summary-bot/recipients_telegram.json"
TOLERANCE_MINUTES = 10  # 허용 오차 범위 (분 단위)

def load_recipients(filepath=RECIPIENTS_PATH):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_telegram_recipients():
    try:
        with open(TELEGRAM_RECIPIENTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []        

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

    # ✅ 이메일 전송
    for person in targets:
        name = person.get("name", "수신자")
        email = person["email"]
        logger.info(f"📬 {name} ({email})에게 메일 전송 중...")

        body = build_email_body(news_data, notion_url, email, name)
        send_email(sender_email, sender_app_password, email, subject, body)

    logger.info("✅ 전체 이메일 전송 완료")

    # ✅ 텔레그램 메시지: 카테고리별로 3번 전송
    # 📲 텔레그램 메시지 전송 시작
    category_map = defaultdict(list)
    for article in news_data:
        category_map[article["category"]].append(article)

    telegram_targets = [r for r in load_telegram_recipients() if r.get("subscribed", True)]

    logger.info(f"📲 텔레그램 구독자 {len(telegram_targets)}명에게 전송 시작")

    for category, articles in category_map.items():
        text = build_telegram_message(articles, max_articles=10)
        for person in telegram_targets:
            chat_id = person["chat_id"]
            send_telegram_message(
                text=text,
                bot_token=telegram_bot_token,
                chat_id=chat_id
            )
            logger.info(f"✅ 텔레그램 전송 완료: {category} → {chat_id}")
            time.sleep(1)  # API 요청 제한 방지

    logger.info("✅ 전체 텔레그램 전송 완료")