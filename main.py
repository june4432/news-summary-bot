### 📁 main.py
from rss import get_latest_news_urls
from crawler import crawl_news
from fast_news_crawler import crawl_multiple_news  # ✅ 병렬 크롤링 함수로 교체
from summarizer import summarize_news_via_api
from notion_writer import save_to_notion, get_existing_urls_from_notion
from mailer import build_email_body, send_email, get_email_subject
from bulk_mailer import send_bulk_email
from config import (
    api_key, notion_token, notion_database_id,
    sender_email, sender_app_password,
    recipient_email, notion_url
)
import datetime
from log import logger
import json
import os

logger.info("뉴스레터 발송 작업 시작!!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RSS_SOURCES_FILE = os.path.join(BASE_DIR, "rss_sources.json")

def load_rss_sources():
    with open(RSS_SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

rss_sources = load_rss_sources()

news_data = []
existing_urls = get_existing_urls_from_notion(notion_token, notion_database_id)

logger.info("노션 가져오기 완료")

for item in rss_sources:
    source = item["source"]  # 예: "매일경제 - 경제"
    category = item["category"]
    rss_url = item["url"]

    print(f"{source} - {category} - {rss_url}")
    
    urls = get_latest_news_urls(rss_url)

    for url in urls:

        logger.info(f"🌐 [{category}] 크롤링 시작: {url}")

        
        article = crawl_news(url)

        if "Content not found" in article['content'] or article['title'] == "ERROR":
            logger.warning(f"⛔ 크롤링 실패로 제외됨: {article['url']}")
            continue

        logger.info(f"✅ 크롤링 성공: {article['title']}")

        if article['url'] in existing_urls:
            continue  # 이미 저장된 뉴스는 스킵

        try:
            result = summarize_news_via_api(article['title'], article['content'], api_key)

            # 결과가 튜플이 아니거나, 길이가 3이 아니면 스킵
            if not isinstance(result, tuple) or len(result) != 3:
                logger.warning(f"⚠️ 요약 형식 이상으로 제외됨: {article['url']}, result={result}")
                continue

            summary, tags, emoji = result

            # 요약 실패인 경우도 건너뜀
            if summary == "요약 실패":
                logger.warning(f"⚠️ 요약 실패로 제외됨: {article['url']}")
                continue

        except Exception as e:
            logger.error(f"❌ 요약 중 예외 발생: {article['url']} / {str(e)}", exc_info=True)
            continue

        article['category'] = category
        article['source'] = source
        
        article['summary'] = summary
        article['tags'] = tags
        article['emoji'] = emoji
        
        

        news_data.append(article)

        logger.info(f"🎯 요약 완료 및 기사 추가됨: {article['url']}")

# ✅ 노션 저장
for article in news_data:
    save_to_notion(article, notion_token, notion_database_id)

# ✅ 메일 + 텔레그램 발송
send_bulk_email(news_data)

logger.info("뉴스레터 발송 작업 완료!!!")