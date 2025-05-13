import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from urllib.parse import quote
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "ai.newsbot.official@gmail.com"
SMTP_PASS = "wduwsdxocutwfyiu"

def send_magic_link_email(email, token):
    encoded_email = quote(email)
    magic_link = f"https://leeyoungjun.duckdns.org/preferences?email={encoded_email}&token={token}"

    content = f"""
    <div style="font-family: 'Segoe UI', 'Noto Sans KR', sans-serif; max-width: 600px; margin: auto; background: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
      <h2 style="color: #1a73e8; margin-top: 0;">🔐 뉴스레터 수신 설정 링크</h2>
      <p style="font-size: 15px; color: #333;">안녕하세요!</p>
      <p style="font-size: 15px; color: #333;">아래 버튼을 클릭하시면 뉴스레터 수신 시간대를 설정하실 수 있습니다. ⏰</p>
      <div style="margin: 24px 0;">
        <a href="{magic_link}" style="background: #34a853; color: white; padding: 12px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 15px;">
          👉 수신 시간 설정하기
        </a>
      </div>
      <p style="font-size: 13px; color: #777;">⚠️ 이 링크는 <strong>10분간만 유효</strong>합니다.</p>
      <p style="font-size: 13px; color: #777;">감사합니다. 😊</p>
    </div>
    """

    msg = MIMEText(content, _charset="utf-8")
    msg["Subject"] = "🔐 뉴스레터 수신 설정 링크"
    msg["From"] = formataddr(("뉴스봇", SMTP_USER))
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
        print(f"✅ 메일 전송 완료 → {email}")
    except Exception as e:
        print(f"❌ 메일 전송 실패 → {email}\n{e}")