import requests
import re
import datetime
from batch.common.log import logger
from batch.telegram.telegram_formatter import escape_markdown_v2

import json

# 뉴스 본문 요약을 위한 챗지피티 호출 api
def summarize_news_via_api(title, content, api_key):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
너는 뉴스 기사를 읽고 기사를 분석하는 전문가야.
기사의 제목과 본문을 분석하한 후 아래 내용을 참조하여 결과를 만들어줘.
반드시 JSON 형식으로 응답해야 해. **코드블럭 없이 순수 JSON**으로만 응답해.
3줄 요약은 불렛 포인트 형식으로 **명사형** 또는 **동명사형** 표현을 사용할 것
기사의 내용을 가장 잘 표현하는 이모지를 emoji에 담을 것.
기사 내용을 포괄하는 주요 키워드 3개를 추출해서 tags를 채울 것.
기사의 내용이 특정 상품/서비스/기업을 홍보하거나 구매/이용을 유도하는 내용이 주를 이루는 경우에 따라 true or false로 표현할 것.
이 기사의 핵심 주제를 나타내는 키워드 1개를 명사형 혹은 동명사형으로 추출해 keyword에 담을 것.
핵심 키워드에 대한 기사의 분위기를 긍정/부정/중립 으로 분석하여 mood에 담을 것.

제목: "{title}"
본문:
\"\"\"
{content}
\"\"\"

아래 형식에 맞춰 응답해:

{{
  "summary": [
    "- 줄거리 요약 첫 줄",
    "- 줄거리 요약 둘째 줄",
    "- 마지막 요약 줄"
  ],
  "tags": ["금융", "정책자금", "소상공인"],
  "emoji": "📰",
  "is_ad": true or false,
  "keyword":"소상공인대출",
  "mood","긍정/중립/부정"
}}
"""

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.6
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
            keyword = result.get("keyword", "")
            mood = result.get("mood", "")

            summary_text = "\n".join(summary_lines)
            logger.info(f"📄 요약: {summary_text}")
            logger.info(f"🏷️ 태그: {tags}")
            logger.info(f"✨ 이모지: {emoji}")
            logger.info(f"📢 광고 여부: {is_ad}")
            logger.info(f"🔑 키워드: {keyword}")
            logger.info(f"📒 분위기: {mood}")

            return summary_text, tags, emoji, is_ad, keyword, mood

        except json.JSONDecodeError as e:
            logger.error("❌ JSON 파싱 실패", exc_info=True)
            logger.error(f"🧾 GPT 응답 원본: {raw}")
            return "요약 실패", [], "❓"

    else:
        logger.error(f"❌ GPT 호출 오류: {response.status_code} {response.text}", exc_info=True)
        return "요약 실패", [], "❓"