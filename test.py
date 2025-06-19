from mailer import send_email, build_email_body, get_email_subject
from token_manager import generate_token


token = generate_token("june4432%2Bnewsbot@icloud.com")

print(token)


# 가짜 뉴스 데이터 샘플
# news_data = [
#     {
#         "title": "무신사 스탠다드, 인천 송도에 첫 오프라인 매장낸다 - 매일경제",
#         "summary": "- 무신사 스탠다드가 인천 송도에 첫 오프라인 매장을 24일 오픈 예정\n- 매장은 330평 규모로 다양한 패션 및 뷰티 상품을 선보일 계획\n- 오픈 기념 이벤트로 할인 및 사은품 제공 예정 🎉",
#         "url": "https://www.mk.co.kr/news/economy/11298917"
#     },
#     {
#         "title": "무신사 스탠다드, 인천 송도에 첫 오프라인 매장낸다 - 매일경제",
#         "summary": "- 무신사 스탠다드가 인천 송도에 첫 오프라인 매장을 24일 오픈 예정\n- 매장은 330평 규모로 다양한 패션 및 뷰티 상품을 선보일 계획\n- 오픈 기념 이벤트로 할인 및 사은품 제공 예정 🎉",
#         "url": "https://www.mk.co.kr/news/economy/11298917"
#     }    
# ]

# # Notion 링크 더미
# notion_url = "https://www.notion.so/1deee7ef42c9803191dae7efd68b2c9d"

# # 메일 정보
# sender_email = "leetop4432@gmail.com"
# sender_app_password = "lqvgrcxttcgvlvtx"
# recipient_email = "june4432@icloud.com"

# # 전송
# subject = get_email_subject()
# body = build_email_body(news_data, notion_url)
# send_email(sender_email, sender_app_password, recipient_email, subject, body)