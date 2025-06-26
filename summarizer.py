import requests
import re
import datetime
from log import logger
from telegram_formatter import escape_markdown_v2  # 너가 만든 함수 import

def summarize_news_via_api(title, content, api_key):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
## 역할
- 당신은 경제, 사회, 국제에 능통한 전문가입니다. 기사 제목과 본문을 보고 기사를 요약해주면 됩니다.
## 출력 스타일
- 불렛포인트 형식으로 작성할 것
- 서술형 대신 **명사형** 또는 **동명사형** 표현 사용 (예: "~할 것", "~함")
- 줄마다 한 줄 요약으로 끝낼 것. 줄바꿈 없이 끝에 이모지 1개를 붙일 것
- 전체 요약은 3줄 이하
- 마지막 줄에는 관련 태그를 JSON 배열로 반환 (예: ["금융", "정책자금", "소상공인"])

제목: {title}
본문: {content}
요약:
"""

import requests
import json
import datetime
from log import logger

def summarize_news_via_api(title, content, api_key):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
너는 경제, 사회, 국제 분야의 전문가야. 
아래 뉴스 기사 제목과 본문을 분석하고 3줄로 요약해줘. 
반드시 JSON 형식으로 응답해야 해. **코드블럭 없이 순수 JSON**으로만 응답해.
서술형 대신 **명사형** 또는 **동명사형** 표현 사용 (예: "~할 것", "~함")
기사를 가장 잘 표현하는 이모지를 emoji에 담을 것.
기사는 명백한 광고, 홍보성 기사일 경우 `"is_ad": true`로 표시해. 그 외엔 false로.

제목: "{title}"
본문:
\"\"\"
{content}
\"\"\"

아래 형식에 맞춰 응답해:

{{
  "summary": [
    "줄거리 요약 첫 줄",
    "줄거리 요약 둘째 줄",
    "마지막 요약 줄"
  ],
  "tags": ["금융", "정책자금", "소상공인"],
  "emoji": "📰",
  "is_ad": true or false
}}
"""

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    logger.info(f"🔍 GPT 요약 요청 시작...")
    logger.info(f"요약 대상 제목: {title}")
    content_preview = content[:200].replace('\n', ' ') + ("..." if len(content) > 200 else "")
    logger.info(f"본문 일부: {content_preview}")

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        raw = response.json()['choices'][0]['message']['content'].strip()

        try:
            result = json.loads(raw)  # 🔐 JSON 파싱 시도
            summary_lines = result.get("summary", [])
            tags = result.get("tags", [])
            emoji = result.get("emoji", "")
            is_ad = result.get("is_ad", False)  # ✅ 광고 여부

            summary_text = "\n".join(summary_lines)
            logger.info(f"📄 요약: {summary_text}")
            logger.info(f"🏷️ 태그: {tags}")
            logger.info(f"✨ 이모지: {emoji}")
            logger.info(f"📢 광고 여부: {is_ad}")

            return summary_text, tags, emoji, is_ad

        except json.JSONDecodeError as e:
            logger.error("❌ JSON 파싱 실패", exc_info=True)
            logger.error(f"🧾 GPT 응답 원본: {raw}")
            return "요약 실패", [], "❓"

    else:
        logger.error(f"❌ GPT 호출 오류: {response.status_code} {response.text}", exc_info=True)
        return "요약 실패", [], "❓"