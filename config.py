from dotenv import load_dotenv
import os

load_dotenv('/home/pi/project/news-summary-bot/.env')  # .env 파일에서 환경변수 로드

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