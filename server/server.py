from flask import Flask, request, jsonify, send_from_directory, redirect, render_template_string
import json
import os
import requests
from datetime import datetime, timedelta
from threading import Thread
import secrets
from urllib.parse import quote
from send_magic_link_email import send_magic_link_email

app = Flask(__name__)
RECIPIENTS_FILE = "../recipients_email.json"
TELEGRAM_RECIPIENTS_FILE = "../recipients_telegram.json"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, data=data)
    print(response.json())  # 또는 logger.info(response.json())

# Load recipients from file or initialize empty list
def load_recipients():
    if os.path.exists(RECIPIENTS_FILE):
        with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save updated recipients list
def save_recipients(data):
    with open(RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_recipients_telegram():
    try:
        with open(TELEGRAM_RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_recipients_telegram(data):
    with open(TELEGRAM_RECIPIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 랜딩페이지에서 구독 기능
@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    time_slots = data.get("time_slots", [])  # ✅ time_slots 받아오기

    if not name or not email:
        return jsonify({"error": "이름과 이메일은 필수입니다. 🔥"}), 400

    recipients = load_recipients()
    if any(r["email"] == email for r in recipients):
        return jsonify({"message": "이미 구독 중입니다. 👍"}), 200

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recipients.append({
        "name": name,
        "email": email,
        "subscribed_at": timestamp,
        "time_slots": time_slots  # ✅ 시간대도 함께 저장
    })
    print(f"✅ 개인 페이지 수정 → {recipients}")
    save_recipients(recipients)
    return jsonify({"message": "구독이 완료되었습니다. 🎉"}), 200

# 랜딩페이지에서 구독해제 기능
@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "이메일은 필수입니다."}), 400

    recipients = load_recipients()
    updated = [r for r in recipients if r["email"] != email]

    if len(updated) == len(recipients):
        return jsonify({"message": "해당 이메일은 구독 목록에 없습니다."}), 404

    print(f"구독 해제 신청 → {email}")

    save_recipients(updated)
    return jsonify({"message": "구독이 해제되었습니다."}), 200

# 메일에서 구독해제 버튼을 눌렀을 때 액션
@app.route("/unsubscribe-button")
def unsubscribe_button():
    email = request.args.get("email")
    if not email:
        return "<h3>잘못된 요청입니다. 이메일이 없습니다.</h3>", 400

    recipients = load_recipients()
    updated = [r for r in recipients if r["email"] != email]
    save_recipients(updated)

    if len(updated) == len(recipients):
        return send_from_directory('.', 'time_expired.html')

    print(f"이메일 구독 해제 버튼 클릭 → {email}")

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>구독 해제 완료</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f9f9f9;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                display: inline-block;
            }}
            .btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #1a73e8;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📮 구독이 해제되었습니다.</h2>
            <p><strong>{email}</strong> 주소의 뉴스레터 구독이 성공적으로 해제되었어요.</p>
            <a class="btn" href='/news-bot?tab=subscribe'>다시 구독하러 가기</a>
        </div>
    </body>
    </html>
    """



# 메일에서 뉴스링크 클릭 시 - 노션페이지가져오기 -> 조회수 증가 -> 본문 링크 리다이렉트
@app.route("/news-click")
def news_click():
    article_url = request.args.get("url")
    if not article_url:
        return "Invalid URL", 400

    # ✅ page_id 먼저 찾아야 함
    page_id = get_page_id_by_url(article_url)  # ← 올바른 Notion 페이지 ID
    if page_id:
        Thread(target=increment_view_count, args=(page_id,)).start()
    else:
        print("❌ 페이지 ID를 찾을 수 없음")

    # 바로 리디렉션
    return redirect(article_url)

# 메일에서 뉴스링크 클릭 시 - 본문 링크로 노션페이지id 가져오기
def get_page_id_by_url(article_url):
    #print(f"🔍 [조회 시작] URL 검색: {article_url}")
    print(f"🔍 [조회 시작] URL 검색: {article_url}")

    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    has_more = True
    next_cursor = None

    while has_more:
        payload = {"start_cursor": next_cursor} if next_cursor else {}

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print("📦 Notion 응답 구조:\n", json.dumps(data, indent=2, ensure_ascii=False))

        for result in data.get("results", []):
            props = result.get("properties", {})
            stored_url = props.get("기사 링크", {}).get("url")

            print(f"🔎 Notion URL 확인 중: {stored_url}")
            stored_url = props.get("기사 링크", {}).get("url")
            if stored_url and stored_url.rstrip('/') == article_url.rstrip('/'):
                print(f"🎯 매치 성공! page_id = {result['id']}")
                return result["id"]

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    print(f"❌ 매치 실패 - URL이 DB에 존재하지 않음")
    return None

# 메일에서 뉴스링크 클릭 시 - 조회수 증가
def increment_view_count(page_id):
    print(f"🆙 조회수 증가 시도 중... 페이지 ID: {page_id}")

    notion_token = os.getenv("NOTION_TOKEN")
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
        res.raise_for_status()
        props = res.json()["properties"]
        curr_raw = props.get("조회수", {}).get("number", 0)
        curr_count = curr_raw if curr_raw is not None else 0

        print(f"👁 기존 조회수: {curr_count}")

        data = {
            "properties": {
                "조회수": {"number": curr_count + 1}
            }
        }

        patch_res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=data)
        patch_res.raise_for_status()
        print(f"✅ 조회수 업데이트 완료! → {curr_count + 1}")

    except Exception as e:
        print(f"❌ 조회수 업데이트 실패: {e}")



# 뉴스레터 구독 랜딩 페이지
@app.route("/news-bot")
def index():
    return send_from_directory(".", "index.html")



# 사용자별 뉴스레터 수신시간 설정을 위한 10분 로그인 랜딩 페이지
@app.route("/login-request")
def login_request():
    return send_from_directory(".", "login-request.html")    

login_tokens = {}  # 메모리 저장

# 사용자별 뉴스레터 수신시간 설정을 위한 10분 로그인 링크 보내기
@app.route("/send-magic-link", methods=["POST"])
def send_magic_link():
    email = request.get_json().get("email")

    allowed_emails = load_recipients()

    # ✅ 이메일이 허용된 목록에 있는지 확인
    if not any(r["email"] == email for r in allowed_emails):
        return jsonify({"message": "등록되지 않은 이메일입니다."}), 200

    token = secrets.token_urlsafe(16)
    expiry = datetime.utcnow() + timedelta(minutes=10)
    login_tokens[email] = {"token": token, "expiry": expiry}

    send_magic_link_email(email, token)  # ✅ 여기서 호출

    # ✅ POST 응답 후 GET 요청을 리디렉션으로 처리
    return jsonify({"message": "메일이 전송되었습니다."})



# 사용자 메일 수신 시간 설정 링크
@app.route("/preferences")
def preferences():
    email = request.args.get("email")
    token = request.args.get("token")

    entry = login_tokens.get(email)
    if not entry or token != entry['token'] or datetime.utcnow() > entry['expiry']:
        return send_from_directory('.', '401.html'), 401        
    
    return send_from_directory('.', 'preferences.html')

# 사용자의 메일 수신 시간 정보 가져오기 
@app.route("/get-preferences", methods=["GET"])
def get_preferences():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "이메일이 없습니다"}), 400

    recipients = load_recipients()
    for person in recipients:
        if person["email"] == email:
            return jsonify({
                "name": person.get("name", ""),
                "time_slots": person.get("time_slots", [])
            }), 200

    return jsonify({"name": "", "time_slots": []})  # 신규 유저 or 설정 없음

# 사용자의 메일 수신 시간 정보 업데이트하기
@app.route("/update-preferences", methods=["POST"])
def update_preferences():
    data = request.get_json()
    email = data.get("email")
    selected_times = data.get("time_slots", [])
    name = data.get("name", "")  # 닉네임 추가

    recipients = load_recipients()
    for person in recipients:
        if person['email'] == email:
            person['time_slots'] = selected_times
            person['name'] = name  # 닉네임 업데이트
            break
    else:
        recipients.append({"email": email, "time_slots": selected_times, "name": name})

    save_recipients(recipients)
    return jsonify({"message": "설정이 저장되었습니다 ✅"})



# robots.txt 제공 라우트 추가
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('.', 'robots.txt')  # 현재 디렉토리 기준

@app.route("/news-bot/")  # ← 이거도 추가해두는게 좋음
def news_bot_slash():
    return redirect("/news-bot")

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    recipients = load_recipients_telegram()

    if text == "/start":
        existing = next((r for r in recipients if r["chat_id"] == chat_id), None)

        if existing:
            if existing.get("subscribed", True):
                send_message(chat_id, "🙌 이미 뉴스 구독 중입니다. 매일 아침 뉴스가 발송됩니다!")
            else:
                existing["subscribed"] = True
                save_recipients_telegram(recipients)
                send_message(chat_id, "✅ 구독을 다시 시작했습니다. 다음 스케줄부터 뉴스가 발송됩니다!")
        else:
            recipients.append({"chat_id": chat_id, "subscribed": True})
            save_recipients_telegram(recipients)
            send_message(chat_id,
                "👋 안녕하세요! 경제 뉴스 요약 봇입니다.\n\n"
                "📰 매일 아침 주요 뉴스가 요약되어 도착합니다!\n"
                "/stop - 뉴스 수신 중지\n"
                "/status - 구독 상태 확인\n"
            )

    elif text == "/stop":
        for r in recipients:
            if r["chat_id"] == chat_id:
                r["subscribed"] = False
        save_recipients_telegram(recipients)
        send_message(chat_id, "⛔️ 뉴스 구독이 해제되었습니다.")
    
    elif text == "/status":
        user = next((r for r in recipients if r["chat_id"] == chat_id), None)
        if user and user.get("subscribed", True):
            send_message(chat_id, "✅ 현재 뉴스 구독 중입니다.")
        else:
            send_message(chat_id, "❌ 구독되어 있지 않습니다. /start 로 다시 시작하세요.")

    elif text == "/help":
        help_message = (
            "🆘 도움말\n\n"
            "/start - 뉴스 구독 시작\n"
            "/stop - 뉴스 구독 중지\n"
            "/status - 내 구독 상태 확인\n"
            "/help - 이 메시지 보기"
        )
        send_message(chat_id, help_message)

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
#    app.run(host="127.0.0.1", port=9000, debug=True)
    app.url_map.strict_slashes = False