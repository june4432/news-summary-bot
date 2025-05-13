import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from collections import defaultdict
from urllib.parse import quote
from log import logger
from config import newsletter_url 
from email.utils import formataddr

def send_email(sender, app_password, recipient, subject, body):
    try:
        msg = MIMEText(body, "html", _charset="utf-8")
        msg['Subject'] = subject
        msg['From'] = formataddr(("AI뉴스봇🤖", sender))
        msg['To'] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_password)
            server.send_message(msg)

        logger.info(f"📧 메일 발송 완료: {recipient}")
    except Exception as e:
        logger.exception(f"❌ 메일 발송 실패 ({recipient}) → {e}")

def build_email_body(news_data, notion_url, recipient_email, recipient_name):
    html = f"""
            <p style="font-size: 16px;">
            안녕하세요 <strong>{recipient_name}</strong>님 👋
            </p>
            <p style="font-size: 14px; color: #555; margin-top: 0; margin-bottom: 24px;">
            카테고리별로 최근 뉴스 10개를 <strong>AI가 요약했어요.</strong><br>
            세상의 흐름을 빠르게 읽어보세요. 🌍
            </p>
            """

    categorized = defaultdict(list)
    for article in news_data:
        categorized[article.get("category", "기타")].append(article)

    for category, articles in categorized.items():
        html += f"<h2 style='margin-top: 40px; margin-bottom: 12px; font-size: 20px; border-bottom: 2px solid #1a73e8; padding-bottom: 4px;'>🗂️ {category} 뉴스</h2>"
        for idx, article in enumerate(articles, start=1):
            summary_html = article['summary'].replace('\n', '<br>')
            tag_html = f"<div style='color: #888; font-size: 13px; margin-top: 4px;'>#" + " #".join(article.get('tags', [])) + "</div>" if article.get('tags') else ""
            html += f"""
            <div style='margin-bottom: 24px;'>
                <div style='font-size:16px; font-weight:bold; line-height: 1.4;'>
                    {idx}. {article['title']}
                </div>
                <div style='line-height: 1.6; margin-top: 2px;'>
                    {summary_html}
                </div>
                {tag_html}
                <a href="{newsletter_url}/news-click?url={article['url']}" style="display:inline-block; margin-top:8px; padding:6px 12px; background:#1a73e8; color:white; border-radius:4px; text-decoration:none; font-size:13px;">
                📄 본문 보러가기
                </a>
            </div>
            """

    unsubscribe_email = quote(recipient_email) # ➜ xxx%2Bnewsbot@gmail.com
    
    html += f"""
        <div style="text-align: center; margin-top: 40px;">
            <a href="{newsletter_url}/login-request" 
            style="display:inline-block; margin:4px; padding:10px 16px; background:#34a853; color:white; border-radius:6px; text-decoration:none; font-size:14px; font-weight:bold;">
                ⏰ 수신 시간 설정
            </a>
            <a href="{notion_url}" 
            style="display:inline-block; margin:4px; padding:10px 16px; background:#5f6368; color:white; border-radius:6px; text-decoration:none; font-size:14px; font-weight:bold;">
                📚 지난 기사 보기
            </a>
            <a href="{newsletter_url}/unsubscribe-button?email={unsubscribe_email}" 
            style="display:inline-block; margin:4px; padding:10px 16px; background:#d93025; color:white; border-radius:6px; text-decoration:none; font-size:14px; font-weight:bold;">
                ❌ 구독 해제
            </a>
        </div>
    """ 

    return html

def get_email_subject():
    now = datetime.now()
    return f"현시각 주요 뉴스 - {now.strftime('%m.%d %H:%M')}"