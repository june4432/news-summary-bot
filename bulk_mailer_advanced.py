import json
import datetime
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
from collections import defaultdict

RECIPIENTS_PATH = "/home/pi/project/news-summary-bot/recipients_email.json"
TELEGRAM_RECIPIENTS_PATH = "/home/pi/project/news-summary-bot/recipients_telegram.json"
TOLERANCE_MINUTES = 30
TELEGRAM_MAX_MESSAGES = 5

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

def group_news_by_full_category(news_data):
    """
    뉴스 데이터를 '신문사::카테고리' 기준으로 그룹핑
    """
    grouped = defaultdict(list)
    for article in news_data:
        source = article.get("source")
        category = article.get("category")
        if source and category:
            key = f"{source}::{category}"
            grouped[key].append(article)
    return grouped

def send_bulk_email(news_data):
    recipients = load_recipients()
    now_key = get_time_key()
    targets = filter_recipients_by_time_slot(recipients, now_key)

    subject = get_email_subject()
    logger.info(f"⏰ 현재 시각: {now_key} 기준으로 대상자 {len(targets)}명 필터링 (±{TOLERANCE_MINUTES}분 허용)")

    # 🔁 뉴스 데이터를 '신문사::카테고리' 기준으로 그룹핑
    news_by_full_category = group_news_by_full_category(news_data)

    # 📬 사용자별 뉴스 필터링 및 전송
    for person in targets:
        name = person.get("name", "수신자")
        email = person["email"]
        selected_keys = person.get("categories", [])

        # 관심 키워드(신문사::카테고리)에 해당하는 뉴스만 추출
        personalized_news = []
        for key in selected_keys:
            personalized_news.extend(news_by_full_category.get(key, []))

        if not personalized_news:
            logger.info(f"⚠️ {name} ({email})님에게 전송할 뉴스가 없습니다. 스킵합니다.")
            continue

        logger.info(f"📬 {name} ({email})님에게 뉴스 {len(personalized_news)}개 전송 중...")
        body = build_email_body(personalized_news, notion_url, email, name)
        send_email(sender_email, sender_app_password, email, subject, body)

    logger.info("✅ 전체 이메일 전송 완료")

    # 📲 텔레그램 전송 (전체 기사 대상으로 수행)
    send_bulk_telegram(news_data)



def send_bulk_telegram(news_data):
    """
    전체 뉴스 기사 중 source-category 단위로 묶어 텔레그램 발송
    각 수신자에게 최대 5개까지만 전송
    """
    source_category_map = defaultdict(list)
    for article in news_data:
        source = article.get("source", "Unknown")
        category = article.get("category", "Unknown")
        key = f"{source} - {category}"
        source_category_map[key].append(article)

    telegram_targets = [r for r in load_telegram_recipients() if r.get("subscribed", True)]
    logger.info(f"📲 텔레그램 구독자 {len(telegram_targets)}명에게 전송 시작")

    # 각 사용자별 메시지 전송 횟수 저장
    message_counts = defaultdict(int)

    for source_category, articles in source_category_map.items():
        text = build_telegram_message(articles, max_articles=10, header=source_category)

        for person in telegram_targets:
            chat_id = person["chat_id"]

            if message_counts[chat_id] >= TELEGRAM_MAX_MESSAGES:
                continue  # 이 사람은 이미 5개 보냄

            send_telegram_message(
                text=text,
                bot_token=telegram_bot_token,
                chat_id=chat_id
            )
            message_counts[chat_id] += 1
            logger.info(f"✅ 텔레그램 전송 완료: {source_category} → {chat_id}")
            time.sleep(1)

    logger.info("✅ 전체 텔레그램 전송 완료")