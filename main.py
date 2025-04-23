### 📁 main.py
from rss import get_latest_news_urls
from crawler import crawl_news
from summarizer import summarize_news_via_api
from notion_writer import save_to_notion, get_existing_urls_from_notion
from mailer import build_email_body, send_email, get_email_subject
from config import api_key, notion_token, database_id, sender_email, sender_app_password, recipient_email, notion_url  # recipient_email can be comma-separated

rss_sources = [
    ("헤드라인", "https://www.mk.co.kr/rss/30000001/"),
    ("경제", "https://www.mk.co.kr/rss/30100041/"),
    ("국제", "https://www.mk.co.kr/rss/30300018/")
]

news_data = []
existing_urls = get_existing_urls_from_notion(notion_token, database_id)

for category, rss_url in rss_sources:
    urls = get_latest_news_urls(rss_url)

    for url in urls:
        article = crawl_news(url)

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
    save_to_notion(article, notion_token, database_id)

subject = get_email_subject()
email_body = build_email_body(news_data, notion_url)  # ✅ 한번만 생성
for recipient in recipient_email.split(','):
    send_email(sender_email, sender_app_password, recipient.strip(), subject, email_body)