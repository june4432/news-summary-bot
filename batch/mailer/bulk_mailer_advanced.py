import json
import datetime
import time
from collections import defaultdict

from batch.mailer.mailer import send_email, get_email_subject, build_email_body
from batch.common.config import (
    sender_email, sender_app_password,
    notion_url, telegram_chat_id, torelance_minutes
)
from batch.common.log import logger
from batch.telegram.telegram import send_telegram_message
from batch.telegram.telegram_formatter import build_telegram_message
from batch.util.recipients_manager import load_recipients, load_recipients_telegram

TOLERANCE_MINUTES = int(torelance_minutes)

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
    now_key = get_time_key()
    telegram_targets = filter_recipients_by_time_slot(load_recipients_telegram(), now_key)
    logger.info(f"📲 텔레그램 수신자 {len(telegram_targets)}명 (⏰ {now_key} 기준)")

    # 🔁 뉴스 데이터를 '신문사::카테고리' 기준으로 그룹핑
    news_by_full_category = group_news_by_full_category(news_data)


    for person in telegram_targets:
        chat_id = person.get("chat_id")
        name = person.get("first_name", "")
        selected_keys = person.get("categories", [])

        for key in selected_keys:

            articles = news_by_full_category.get(key, [])
            if not articles:
                continue

            text = build_telegram_message(articles, max_articles=10, header=key.replace("::", " - "))
            print(f"[디버깅] 전송 대상: {key} / 기사 수: {len(articles)}")
            print(f"[본문 내용]\n{text}\n")
            send_telegram_message(
                text=text,
                chat_id=chat_id
            )
            logger.info(f"✅ 텔레그램 전송: {key} → {chat_id}")
            time.sleep(1)

    logger.info("✅ 텔레그램 맞춤 전송 완료")