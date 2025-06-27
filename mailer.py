import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from collections import defaultdict
from urllib.parse import quote
from log import logger
from config import newsletter_url 
from email.utils import formataddr
from token_manager import generate_token

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
<div style="font-family: 'Segoe UI', 'Noto Sans KR', sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
  <p style="font-size: 16px; margin: 0 0 12px 0;">
    안녕하세요 <strong>{recipient_name}</strong>님 👋
  </p>

  <p style="margin: 0 0 20px 0;">
    카테고리별로 최근 뉴스 10개를 <strong>AI가 요약했어요.</strong><br>
    세상의 흐름을 빠르게 읽어보세요. 🌍
  </p>

  <p>🔧 본문 맨 아래의 <strong>[개인 구독 설정]</strong> 버튼을 누르면 <u>시간대</u>와 <u>관심 카테고리</u>를 직접 고를 수 있어요.</p>
  <p>📰 신규 카테고리가 추가되었습니다. (매일경제 : 기업·경영, 스포츠, 게임 // 한국경제 : 증권, IT, 오피니언)</p>
  <p>📢 AI가 뉴스를 <strong>광고성 기사</strong>로 판단한 경우, 제목 앞에 <strong>[광고성]</strong> 표시가 붙습니다.</p>
  <p>🎉 텔레그램으로도 뉴스레터를 받아볼 수 있습니다. 👉 <a href="https://t.me/news_epitome_bot" target="_blank" style="color: #1a73e8; text-decoration: none;">텔레그램 열기</a></p>
</div>
"""

    categorized = defaultdict(list)
    for article in news_data:
        display_key = f"{article['source']} - {article['category']}"
        categorized[display_key].append(article)

    # ✅ 본문 생성
    for display_key, articles in categorized.items():
        html += f"<h2 style='margin-top: 40px; margin-bottom: 12px; font-size: 20px; border-bottom: 2px solid #1a73e8; padding-bottom: 4px;'>🗂️ {display_key} 뉴스</h2>"
        for idx, article in enumerate(articles, start=1):
            title = article.get('title', '제목 없음')
            url = article.get('url', '#')
            summary_html = article.get('summary', '').replace('\n', '<br>')
            tag_html = f"<div style='color: #888; font-size: 13px; margin-top: 4px;'>#" + " #".join(article.get('tags', [])) + "</div>" if article.get('tags') else ""
            emoji = article.get('emoji', '')
            is_ad = article.get('is_ad', False)

            # ✅ 광고 표시 추가
            if is_ad:
                title = f"[광고성] {title}"

            html += f"""
            <div style='margin-bottom: 24px;'>
                <div style='font-size:16px; font-weight:bold; line-height: 1.4;'>
                    {idx}. {title} {emoji}
                </div>
                <div style='line-height: 1.6; margin-top: 2px;'>
                    {summary_html}
                </div>
                {tag_html}
                <a href="{newsletter_url}/news-click?url={url}" style="display:inline-block; margin-top:8px; padding:6px 12px; background:#1a73e8; color:white; border-radius:4px; text-decoration:none; font-size:13px;">
                📄 본문 보러가기
                </a>
            </div>
            """

    unsubscribe_email = quote(recipient_email)
    token = generate_token(unsubscribe_email)
    encrypted_link = f"{newsletter_url}/news-settings?token={token}"

    html += f"""
        <div style="text-align: center; margin-top: 40px;">
            <a href="{encrypted_link}" 
            style="display:inline-block; margin:4px; padding:10px 16px; background:#34a853; color:white; border-radius:6px; text-decoration:none; font-size:14px; font-weight:bold;">
                ⚙️ 개인 구독 설정
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