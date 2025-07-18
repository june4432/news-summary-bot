# log.py
import logging

# 기본 설정: 시간, 로그 레벨, 메시지 출력
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("news-bot")