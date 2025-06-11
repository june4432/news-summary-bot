import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from urllib.parse import quote
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SENDER_EMAIL")
SMTP_PASS = os.getenv("SENDER_APP_PASSWORD")

print(SMTP_USER)
print(SMTP_PASS)

def send_magic_link_email(email, token):
    encoded_email = quote(email)
    magic_link = f"https://leeyoungjun.duckdns.org/preferences?email={encoded_email}&token={token}"

    html = f"""\
    <h2 style="color:#1a73e8;">🔐 뉴스레터 수신 설정 링크</h2>
    <p style="font-size:15px; color:#333;">안녕하세요 👋</p>
    <p style="font-size:15px; color:#333;">
        아래 버튼을 클릭하시면 뉴스레터 수신 시간대를 설정하실 수 있습니다. ⏰
    </p>
    <p>
      <a href="{magic_link}" style="display:inline-block; margin:20px 0; background:#34a853; color:white; padding:12px 20px; text-decoration:none; border-radius:6px; font-weight:bold; font-size:15px;">
        👉 수신 시간 설정하기
      </a>
    </p>
    <p style="font-size:13px; color:#777;">⚠️ 이 링크는 <strong>10분간만 유효</strong>합니다.</p>
    <p style="font-size:13px; color:#777;">감사합니다 😊</p>
    """

    msg = MIMEText(html, "html", _charset="utf-8")
    msg["Subject"] = "🔐 뉴스레터 수신 설정 링크"
    msg["From"] = formataddr(("AI뉴스봇🤖", "ai.newsbot.official@gmail.com"))
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
            print(f"✅ 수신정보 설정 메일 전송 완료 → {email}")
    except Exception as e:
        print(f"❌ 수신정보 설정 메일 전송 실패 → {email}\n{e}")