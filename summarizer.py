import requests
import re

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

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    print("\n🔍 GPT 요약 요청 시작...")
    print("요약 대상 제목:", title)
    print("본문 일부:", content[:200].replace('\n', ' ') + ("..." if len(content) > 200 else ""))

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        text = response.json()['choices'][0]['message']['content'].strip()
        print("✅ GPT 요약 완료. 응답 내용:")
        print(text)
        return extract_summary_and_tags(text)
    else:
        print("❌ GPT 호출 오류:", response.status_code, response.text)
        return "요약 실패", []

def extract_summary_and_tags(text):
    parts = text.strip().split('\n')
    summary_lines = []
    tags = []

    for line in parts:
        if line.strip().startswith('[') and line.strip().endswith(']'):
            tag_match = re.search(r"\[(.*?)\]", line)
            if tag_match:
                tags = [t.strip('" ') for t in tag_match.group(1).split(',')]
            break
        else:
            summary_lines.append(line.strip())

    print("📄 추출된 요약:", " ".join(summary_lines))
    print("🏷️ 추출된 태그:", tags)
    return "\n".join(summary_lines), tags