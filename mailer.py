import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from collections import defaultdict
from urllib.parse import quote

def send_email(sender, app_password, recipient, subject, body):
    try:
        msg = MIMEText(body, "html", _charset="utf-8")
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_password)
            server.send_message(msg)

        print(f"📧 메일 발송 완료: {recipient}")
    except Exception as e:
        print(f"❌ 메일 발송 실패 ({recipient}) → {e}")

def build_email_body(news_data, notion_url, recipient_email):
    html = ""
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
                <div style='margin-top: 8px;'>
                    <a href="http://june4432.ipdisk.co.kr:9000/news-click?url={article['url']}" style="color:#1a73e8; text-decoration:none;">본문보러가기</a>
                </div>
            </div>
            """

    unsubscribe_email = quote(recipient_email) # ➜ xxx%2Bnewsbot@gmail.com
    
    html += f"""
    <p><a href="{notion_url}" style="color:#1a73e8; text-decoration:none;">🔗 지난 기사 보러 가기</a></p>
    <div style='text-align:center; margin-top: 32px;'>
        <a href='http://june4432.ipdisk.co.kr:9000/unsubscribe-button?email={unsubscribe_email}' 
        style='display:inline-block; padding:8px 16px; background:#d93025; color:white; border-radius:4px; text-decoration:none; font-size:13px;'>구독 해제하기</a>
    </div>    
    """
    return html

def get_email_subject():
    now = datetime.now()
    return f"현시각 주요 뉴스 - {now.strftime('%m.%d %H:%M')}"