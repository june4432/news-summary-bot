# 📰 News Summary Bot

자동으로 RSS 뉴스를 크롤링하고, GPT를 통해 요약 및 태그를 생성한 후 Notion에 저장하고 이메일로 발송하는 자동화 봇입니다.

## 🚀 기능
- ✅ RSS 기반 뉴스 수집 (카테고리별)
- ✨ GPT-4o-mini 기반 뉴스 요약 및 키워드 태깅
- 🧠 Notion DB에 뉴스 요약 저장 (카테고리, 태그, 본문, 이미지 포함)
- 📬 이메일로 요약 뉴스 전송 (다중 수신자 지원)
- 🔁 중복 뉴스 필터링 (Notion DB 기준)
- 🕒 크론탭을 통한 주기적 실행

## 📁 구조
```
project/
├── main.py                # 전체 흐름 제어
├── rss.py                 # RSS 파싱
├── crawler.py            # 뉴스 본문/이미지 크롤링
├── summarizer.py         # GPT 요약 및 태그 추출
├── notion_writer.py      # Notion 저장
├── mailer.py             # 이메일 발송
├── .env                  # 비밀 환경변수 파일
├── requirements.txt      # 필요한 패키지 목록
```

## 🔧 환경설정
`.env` 파일을 `.env.example` 참고해서 생성해 주세요.

## 🛠 설치 및 실행
```bash
# 가상환경 권장
pip install -r requirements.txt
python main.py
```

## 🕒 자동 실행
```bash
crontab -e
```
예시:
```
30 7 * * * /usr/bin/python3 /home/pi/project/news_summary/main.py
```

## 💡 예시 사용처
- 사내 경제 뉴스 요약봇
- 블로그/뉴스 큐레이션 자동화
- CEO/팀장 대상 이슈 리포트 전송

---

궁금한 점이나 기능 확장은 언제든지 말씀해주세요! 😎