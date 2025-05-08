from flask import Flask, request, jsonify, send_from_directory, redirect, render_template_string
import json
import os
import requests
from datetime import datetime
from threading import Thread

app = Flask(__name__)
RECIPIENTS_FILE = "../recipients.json"

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

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "이름과 이메일은 필수입니다. 🔥"}), 400

    recipients = load_recipients()
    if any(r["email"] == email for r in recipients):
        return jsonify({"message": "이미 구독 중입니다. 👍"}), 200

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recipients.append({"name": name, "email": email, "subscribed_at": timestamp})
    save_recipients(recipients)
    return jsonify({"message": "구독이 완료되었습니다. 🎉"}), 200

@app.route("/unsubscribe")
def auto_unsubscribe():
    email = request.args.get("email")
    if not email:
        return "<h3>⚠️ 이메일 정보가 누락되었습니다.</h3>", 400

    recipients = load_recipients()
    updated = [r for r in recipients if r["email"] != email]

    if len(updated) == len(recipients):
        return f"<h3>📭 {email} 은(는) 구독 중이 아닙니다.</h3><p><a href='/?tab=subscribe'>구독하기</a></p>", 200

    save_recipients(updated)
    return f"<h3>🗑️ {email} 님의 구독이 해제되었습니다.</h3><p><a href='/?tab=subscribe'>다시 구독하기</a></p>", 200

@app.route("/unsubscribe-button")
def unsubscribe_button():
    email = request.args.get("email")
    if not email:
        return "<h3>잘못된 요청입니다. 이메일이 없습니다.</h3>", 400

    recipients = load_recipients()
    updated = [r for r in recipients if r["email"] != email]
    save_recipients(updated)

    if len(updated) == len(recipients):
        return f"<p>뉴스레터 구독 정보가 없는 이메일입니다 : {email}</p>"

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
            <a class="btn" href='/?tab=subscribe'>다시 구독하러 가기</a>
        </div>
    </body>
    </html>
    """

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

    save_recipients(updated)
    return jsonify({"message": "구독이 해제되었습니다."}), 200

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

def get_page_id_by_url(article_url):
    #print(f"🔍 [조회 시작] URL 검색: {article_url}")

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
        #print("📦 Notion 응답 구조:\n", json.dumps(data, indent=2, ensure_ascii=False))

        for result in data.get("results", []):
            props = result.get("properties", {})
            stored_url = props.get("기사 링크", {}).get("url")

            #print(f"🔎 Notion URL 확인 중: {stored_url}")
            stored_url = props.get("기사 링크", {}).get("url")
            if stored_url and stored_url.rstrip('/') == article_url.rstrip('/'):
                #print(f"🎯 매치 성공! page_id = {result['id']}")
                return result["id"]

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    #print(f"❌ 매치 실패 - URL이 DB에 존재하지 않음")
    return None

def increment_view_count(page_id):
    #print(f"🆙 조회수 증가 시도 중... 페이지 ID: {page_id}")

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

        #print(f"👁 기존 조회수: {curr_count}")

        data = {
            "properties": {
                "조회수": {"number": curr_count + 1}
            }
        }

        patch_res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=data)
        patch_res.raise_for_status()
        #print(f"✅ 조회수 업데이트 완료! → {curr_count + 1}")

    except Exception as e:
        print(f"❌ 조회수 업데이트 실패: {e}")

@app.route("/news-bot")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)