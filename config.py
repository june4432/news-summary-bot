from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경변수 로드

api_key = os.getenv("API_KEY")
notion_token = os.getenv("NOTION_TOKEN")
database_id = os.getenv("DATABASE_ID")
sender_email = os.getenv("SENDER_EMAIL")
sender_app_password = os.getenv("SENDER_APP_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")
notion_url = os.getenv("NOTION_URL")