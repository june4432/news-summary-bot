### 📁 main.py
from rss import get_latest_news_urls
from crawler import crawl_news
from summarizer import summarize_news_via_api
from notion_writer import save_to_notion, get_existing_urls_from_notion
from mailer import build_email_body, send_email, get_email_subject
from bulk_mailer import send_bulk_email
from config import api_key, notion_token, notion_database_id, sender_email, sender_app_password, recipient_email, notion_url  # recipient_email can be comma-separated
import datetime
from log import logger

logger.info("뉴스레터 발송 작업 시작!!")
rss_sources = [
    ("헤드라인", "https://www.mk.co.kr/rss/30000001/"),
    ("경제", "https://www.mk.co.kr/rss/30100041/"),
    ("국제", "https://www.mk.co.kr/rss/30300018/")
]

news_data = []
existing_urls = get_existing_urls_from_notion(notion_token, notion_database_id)

for category, rss_url in rss_sources:
    urls = get_latest_news_urls(rss_url)

    for url in urls:
        article = crawl_news(url)

        if "Content not found" in article['content']:
            logger.warning(f"⛔ 크롤링 실패로 제외됨: {url}")
            continue  # 목록에서 제외

        if article['url'] in existing_urls:
            continue  # 이미 보낸 뉴스는 스킵

        result = summarize_news_via_api(article['title'], article['content'], api_key)
        if isinstance(result, tuple) and len(result) == 2:
            summary, tags = result
        else:
            summary, tags = result, []
        article['summary'] = summary
        article['tags'] = tags
        article['category'] = category  # ✅ 카테고리 추가
        news_data.append(article)

for article in news_data:
    save_to_notion(article, notion_token, notion_database_id)

send_bulk_email(news_data)

logger.info("뉴스레터 발송 작업 완료!!!")