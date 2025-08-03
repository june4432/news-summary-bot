### 📁 main.py
import sys
import os
import json
import datetime

# 현재 파일(server.py)의 디렉토리 (backend)
current_server_dir = os.path.dirname(os.path.abspath(__file__))

# 프로젝트의 루트 디렉토리 (news-summary-bot-divide)를 sys.path에 추가
# 이렇게 하면 'backend'와 'batch'를 최상위 패키지처럼 임포트할 수 있습니다.
project_root = os.path.abspath(os.path.join(current_server_dir, '..'))
if project_root not in sys.path: # 중복 추가 방지
    sys.path.append(project_root)

from batch.util.rss import get_latest_news_urls
from batch.crawler.crawler import crawl_news
from batch.summarizer.summarizer_gpt import summarize_news_via_api, detect_language, translate_english_article
from batch.notion_writer.notion_writer import save_to_notion, get_existing_urls_from_notion
from batch.mailer.mailer import build_email_body, send_email, get_email_subject
from batch.mailer.bulk_mailer_advanced import send_bulk_email
from batch.common.config import (
    api_key, notion_token, notion_database_id,
    sender_email, sender_app_password,
    recipient_email, notion_url, rss_sources_file
)
from batch.util.recipients_manager import load_recipients, load_recipients_telegram
from batch.common.log import logger

logger.info("뉴스레터 발송 작업 시작!!")

def load_rss_sources():
    with open(rss_sources_file, "r", encoding="utf-8") as f:
        all_sources = json.load(f)

    # ✅ 이메일 + 텔레그램 사용자 모두 불러오기
    recipients_email = load_recipients()
    recipients_telegram = load_recipients_telegram()
    all_recipients = recipients_email + recipients_telegram

    # ✅ 모든 사용자의 관심 카테고리 추출
    interested_keys = set()
    for person in all_recipients:
        for key in person.get("categories", []):
            interested_keys.add(key)  # 예: "매일경제::국제"

    # ✅ 관심있는 RSS만 필터링
    filtered_sources = []
    for entry in all_sources:
        key = f"{entry['source']}::{entry['category']}"
        if key in interested_keys:
            filtered_sources.append(entry)

    return filtered_sources

news_data = []

logger.info("rss 로딩 시작")
rss_sources = load_rss_sources()
logger.info("rss 로딩 완료")


logger.info("이틀치 노션 데이터베이스 정보 가져오기 시작")
existing_urls = get_existing_urls_from_notion()
logger.info("이틀치 노션 데이터베이스 정보 가져오기 완료")

logger.info("뉴스 카테고리 크롤링 시작")

for item in rss_sources:
    source = item["source"]  # 예: "매일경제 - 경제"
    category = item["category"]
    rss_url = item["url"]

    print(f"{source} - {category} - {rss_url}")
    
    urls = get_latest_news_urls(rss_url)

    for url in urls:

        if url in existing_urls:
            continue  # 이미 저장된 뉴스는 스킵

        logger.info(f"🌐 [{category}] 크롤링 시작: {url}")

        
        article = crawl_news(url)

        if "Content not found" in article['content'] or article['title'] == "ERROR":
            logger.warning(f"⛔ 크롤링 실패로 제외됨: {article['url']}")
            continue

        logger.info(f"✅ 크롤링 성공: {article['title']}")

        # 🌍 언어 감지 및 번역 처리
        language = detect_language(article['title'] + " " + article['content'])
        logger.info(f"🔍 언어 감지 결과: {language}")
        
        # 원본 기사 정보 저장
        article['original_title'] = article['title']
        article['original_content'] = article['content']
        article['language'] = language
        
        # 영어 기사인 경우 번역 수행
        if language == "english":
            try:
                translated_title, translated_content = translate_english_article(
                    article['title'], article['content'], api_key
                )
                article['translated_title'] = translated_title
                article['translated_content'] = translated_content
                
                # 노션 저장 및 요약에는 번역된 내용 사용
                article['title'] = translated_title
                article['content'] = translated_content
                
                logger.info(f"🌍 번역 완료: {translated_title}")
                
            except Exception as e:
                logger.error(f"❌ 번역 중 예외 발생: {article['url']} / {str(e)}", exc_info=True)
                # 번역 실패 시에도 원본으로 계속 진행
                article['translated_title'] = None
                article['translated_content'] = None

        try:
            result = summarize_news_via_api(article['title'], article['content'], api_key)

            summary, tags, emoji, is_ad, keyword, mood = result

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
        article['is_ad'] = is_ad
        article['keyword'] = keyword
        article['mood'] = mood
        
        

        news_data.append(article)

        logger.info(f"🎯 요약 완료 및 기사 추가됨: {article['url']}")

logger.info("뉴스 카테고리 크롤링 종료")

logger.info("노션 저장 시작")
# ✅ 노션 저장
for article in news_data:
    save_to_notion(article, notion_token, notion_database_id)
logger.info("노션 저장 완료")

logger.info("메일 및 텔레그램 발송 시작")
# ✅ 메일 + 텔레그램 발송
send_bulk_email(news_data)
logger.info("메일 및 텔레그램 발송 종료")

logger.info("뉴스레터 발송 작업 완료!!!")