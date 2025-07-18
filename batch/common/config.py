from dotenv import load_dotenv
import os

# .env에 정의되어 있는 환경변수를 로드한다.
load_dotenv('/home/pi/project/news-summary-bot/batch/.env')  # .env 파일에서 환경변수 로드

api_key = os.getenv("API_KEY")
notion_token = os.getenv("NOTION_TOKEN")
notion_database_id = os.getenv("NOTION_DATABASE_ID")
sender_email = os.getenv("SENDER_EMAIL")
sender_app_password = os.getenv("SENDER_APP_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")
notion_url = os.getenv("NOTION_URL")
newsletter_url = os.getenv("NEWSLETTER_URL")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
secret_token_for_login = os.getenv("SECRET_TOKEN_FOR_LOGIN")
torelance_minutes = os.getenv("MSG_SEND_TOLERANCE_MINUTES")
recipients_email_file = os.getenv("RECIPIENTS_EMAIL_FILE")
recipients_telegram_file = os.getenv("RECIPIENTS_TELEGRAM_FILE")
rss_sources_file = os.getenv("RSS_SOURCES_FILE")
rss_batch_count = os.getenv("RSS_BATCH_COUNT")