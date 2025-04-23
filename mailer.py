### 📁 mailer.py
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from collections import defaultdict

def send_email(sender, app_password, recipient, subject, body):
    msg = MIMEText(body, "html", _charset="utf-8")  # HTML 형식으로 전송
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, app_password)
        server.send_message(msg)

    print(f"📧 메일 발송 완료: {recipient}")

def build_email_body(news_data, notion_url):
    html = ""
    categorized = defaultdict(list)
    for article in news_data:
        categorized[article.get("category", "기타")].append(article)

    for category, articles in categorized.items():
        html += f"<h2 style='margin-bottom: 8px;'>{category}</h2>"
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
                    <a href="{article['url']}" style="color:#1a73e8; text-decoration:none;">본문보러가기</a>
                </div>
            </div>
            """

    html += f"""<p>지난 기사 보러 가기 - <a href="{notion_url}">{notion_url}</a></p>"""
    return html

def get_email_subject():
    now = datetime.now()
    return f"현시각 주요 뉴스 - {now.strftime('%m.%d %H:%M')}"