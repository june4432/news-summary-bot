# flask import에서 render_template_string, render_template 제거
from flask import Flask, request, jsonify, send_from_directory, redirect
import json
import os
import requests
from datetime import datetime, timedelta
from threading import Thread
import secrets
from urllib.parse import quote, urlencode, unquote
import jwt
import sys
from collections import defaultdict
from flask_cors import CORS


# 현재 파일(server.py)의 디렉토리 (backend)
current_server_dir = os.path.dirname(os.path.abspath(__file__))

# 프로젝트의 루트 디렉토리 (news-summary-bot-divide)를 sys.path에 추가
# 이렇게 하면 'backend'와 'batch'를 최상위 패키지처럼 임포트할 수 있습니다.
project_root = os.path.abspath(os.path.join(current_server_dir, '..'))
if project_root not in sys.path: # 중복 추가 방지
    sys.path.append(project_root)

from batch.common.token_manager import generate_token
from batch.common.config import rss_sources_file
from batch.telegram.telegram_formatter import escape_markdown_v2
from batch.telegram.telegram import send_message
from batch.util.rss import load_rss_sources
from batch.util.recipients_manager import load_recipients, save_recipients, load_recipients_telegram, save_recipients_telegram
from batch.notion_writer.notion_writer import increment_view_count, get_page_id_by_url

# template_folder 제거
app = Flask(__name__) 
CORS(app, resources={r"/*": {"origins": ["http://june4432.ipdisk.co.kr:5173",
                                         "https://leeyoungjun.duckdns.org",
                                         "http://192.168.0.65:5173",
                                         "http://localhost:5173"
]}})

NEWSLETTER_URL = os.getenv("NEWSLETTER_URL")
SECRET_TOKEN_FOR_LOGIN = os.getenv("SECRET_TOKEN_FOR_LOGIN")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    time_slots = data.get("time_slots", [])
    subscribe_at = data.get("subscribe_at")
    categories = data.get("categories", [])

    if not name or not email:
        return jsonify({"error": "이름과 이메일은 필수입니다. 🔥"}), 400

    # ✅ ::: → ::로 변환
    formatted_categories = [c.replace(":::", "::") for c in categories]

    recipients = load_recipients()
    if any(r["email"] == email for r in recipients):
        return jsonify({"message": "이미 구독 중입니다. 👍"}), 200

    recipients.append({
        "name": name,
        "email": email,
        "time_slots": time_slots,
        "categories": formatted_categories,
        "subscribe_at": subscribe_at or datetime.now().isoformat()
    })

    print(f"✅ 구독 신청 완료 → {email}")
    save_recipients(recipients)
    return jsonify({"message": "구독이 완료되었습니다. 🎉"}), 200

# 랜딩페이지에서 구독해제 기능
@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()
    email = data.get("email")
    unsubscribe_at = data.get("unsubscribe_at")  # ✅ 추가됨

    if not email:
        return jsonify({"error": "이메일은 필수입니다."}), 400

    recipients = load_recipients()
    new_list = []
    found = False

    for r in recipients:
        if r["email"] == email:
            found = True
            print(f"구독 해제 신청 → {email}")
            # ✅ 구독 해제 시간만 남겨놓고 기록은 유지할 수도 있음
            r["unsubscribe_at"] = unsubscribe_at or datetime.now().isoformat()
            r["time_slots"] = []
            r["categories"] = []
            r["name"] = r.get("name", "")
            new_list.append(r)
        else:
            new_list.append(r)

    if not found:
        return jsonify({"message": "해당 이메일은 구독 목록에 없습니다."}), 404

    save_recipients(new_list)
    return jsonify({"message": "구독이 해제되었습니다."}), 200

# 메일에서 구독해제 버튼을 눌렀을 때 액션 (HTML 응답을 JSON으로 변경)
@app.route("/unsubscribe-button")
def unsubscribe_button():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "이메일이 없습니다."}), 400 # JSON 응답

    recipients = load_recipients()
    updated = [r for r in recipients if r["email"] != email]
    
    if len(updated) == len(recipients):
        # 구독 목록에 없는 경우, 404 메시지를 JSON으로 반환
        return jsonify({"message": "해당 이메일은 구독 목록에 없습니다."}), 404 

    save_recipients(updated)
    print(f"이메일 구독 해제 버튼 클릭 → {email}")
    
    # 성공 메시지를 JSON으로 반환
    return jsonify({"message": "구독이 성공적으로 해제되었습니다."}), 200


# 메일에서 뉴스링크 클릭 시 - 노션페이지가져오기 -> 조회수 증가 -> 본문 링크 리다이렉트
@app.route("/news-click")
def news_click():
    article_url = request.args.get("url")
    if not article_url:
        return "Invalid URL", 400

    # ✅ 조회수 처리는 완전히 백그라운드로
    Thread(target=process_click_event, args=(article_url,)).start()

    # ✅ 사용자는 즉시 기사로 리다이렉트
    return redirect(article_url)

def process_click_event(article_url):
    try:
        page_id = get_page_id_by_url(article_url)
        if page_id:
            increment_view_count(page_id)
        else:
            print(f"❌ [조회 실패] URL에 해당하는 Notion page_id 없음: {article_url}")
    except Exception as e:
        print(f"❌ [조회 처리 실패] 예외 발생: {e}")


# 뉴스레터 구독 랜딩 페이지 - React 앱이 담당하므로 이 라우트는 제거하거나, React 빌드 파일을 서빙하도록 변경
# @app.route("/news-bot")
# def index():
#     return send_from_directory(".", "index.html")


@app.route("/get-categories", methods=["GET"])
def get_categories():
    try:
        # server.py 파일의 절대 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 프로젝트 루트 디렉토리 (backend 폴더의 부모)
        project_root = os.path.join(current_dir, '..') 
        
        # data 폴더 내의 rss_sources.json 파일 경로
        rss_sources_path = rss_sources_file

        with open(rss_sources_path, "r", encoding="utf-8") as f:
            sources = json.load(f)

        result = defaultdict(list)
        for item in sources:
            source = item.get("source")
            category = item.get("category")
            if source and category:
                result[source].append(category)

        return jsonify(result), 200
    except Exception as e:
        print("❌ get-categories 오류:", str(e))
        return jsonify({"error": "서버 내부 오류"}), 500

# 사용자의 메일 또는 텔레그램 수신 정보 업데이트
@app.route("/update-preferences", methods=["POST"])
def update_preferences():
    data = request.get_json()
    print("📥 수신 데이터:", data)
    email = data.get("email", "").strip()
    chat_id = str(data.get("chat_id", "")).strip()
    selected_times = data.get("time_slots", [])
    selected_categories = data.get("categories", [])
    name = data.get("name", "")  # 닉네임 or 이름
    modified_at = data.get("modified_at")

    if not email and not chat_id:
        return jsonify({"error": "이메일 또는 chat_id가 필요합니다."}), 400

    # ✅ 이메일 사용자 업데이트
    if email:
        recipients = load_recipients()
        for person in recipients:
            if person.get("email") == email:
                person["time_slots"] = selected_times
                person["categories"] = selected_categories
                person["name"] = name
                person["modified_at"] = modified_at
                break
        else:
            recipients.append({
                "email": email,
                "time_slots": selected_times,
                "categories": selected_categories,
                "name": name,
                "modified_at": modified_at
            })
        save_recipients(recipients)
        return jsonify({"message": "이메일 사용자 설정이 저장되었습니다 ✅"})

    # ✅ 텔레그램 사용자 업데이트
    if chat_id:
        recipients = load_recipients_telegram()
        for person in recipients:
            if str(person.get("chat_id")) == chat_id:
                person["time_slots"] = selected_times
                person["categories"] = selected_categories
                person["modified_at"] = modified_at
                break
        else:
            recipients.append({
                "chat_id": chat_id,
                "first_name": name,
                "time_slots": selected_times,
                "categories": selected_categories,
                "modified_at": modified_at
            })
        save_recipients_telegram(recipients)
        return jsonify({"message": "텔레그램 사용자 설정이 저장되었습니다 ✅"})

@app.route("/get-preferences-by-token", methods=["GET"])
def get_preferences_by_token():
    token = request.args.get("token", "")

    token = request.args.get("token", "")

    result = decode_token_safe(token)

    if not token:
        return jsonify({"error": "Missing token"}), 400

    result = decode_token_safe(token)
    if "error" in result:
        return jsonify({"error": result["error"]}), 400

    payload = result["payload"]
    email = payload.get("email")
    chat_id = payload.get("chat_id")

    # ✅ 1차: 이메일 사용자 조회
    if email:
        email = unquote(email)
        recipients = load_recipients()  # 이메일 사용자 리스트
        for person in recipients:
            if person.get("email") == email:
                return jsonify({
                    "email": person.get("email", ""),
                    "chat_id": "",  # 이메일 사용자에게는 chat_id 없음
                    "name": person.get("name", ""),
                    "time_slots": person.get("time_slots", []),
                    "categories": person.get("categories", [])
                })

    # ✅ 2차: 텔레그램 사용자 조회 (chat_id 기준)
    if chat_id:
        recipients = load_recipients_telegram()  # 텔레그램 사용자 리스트
        for person in recipients:
            # 🔒 반드시 타입 맞춰서 비교 (정수 ↔ 문자열 혼동 방지)
            if str(person.get("chat_id")) == str(chat_id):

                first = person.get("first_name", "")
                last = person.get("last_name", "")
                name = f"{first} {last}".strip()

                return jsonify({
                    "email": "",  # 텔레그램 사용자에게는 이메일 없음
                    "chat_id": person.get("chat_id", ""),
                    "name": name,
                    "time_slots": person.get("time_slots", []),
                    "categories": person.get("categories", [])
                })

    # 사용자를 못 찾은 경우 기본값 반환
    return jsonify({
        "email": email if email else "",
        "chat_id": chat_id if chat_id else "",
        "name": "",
        "time_slots": [],
        "categories": []
    })

def decode_token_safe(token: str):
    # ✅ b'...' 또는 b"..." 형식 제거
    if token.startswith("b'") and token.endswith("'"):
        token = token[2:-1]
    elif token.startswith('b"') and token.endswith('"'):
        token = token[2:-1]

    try:
        payload = jwt.decode(token, SECRET_TOKEN_FOR_LOGIN, algorithms=["HS256"])
        return {"payload": payload, "token": token}  # ✅ 깨끗한 token도 같이 반환
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}



# robots.txt 제공 라우트 추가 - 유지
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('.', 'robots.txt')  # 현재 디렉토리 기준

# /news-bot/ -> /news-bot 리다이렉트 라우트 (React 앱 구성에 따라 제거 또는 수정)
# @app.route("/news-bot/")
# def news_bot_slash():
#     return redirect("/news-bot")

# 텔레그램 웹훅 (백엔드 로직이므로 유지)
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    recipients = load_recipients_telegram()

    token = generate_token(chat_id, is_email=False)
    encrypted_link = f"{NEWSLETTER_URL}/news-settings?token={token}"

    if text == "/start":
        from_user = message.get("from", {})
        first_name = from_user.get("first_name", "")
        last_name = from_user.get("last_name", "")
        username = from_user.get("username", "")

        existing = next((r for r in recipients if r["chat_id"] == chat_id), None)

        if existing:
            if existing.get("subscribed", True):
            
                send_message(
                    chat_id,
                    "🙌 이미 뉴스를 구독하고 계시네요.\n\n"
                    "맞춤 뉴스 설정을 변경하시려면 링크를 눌러\n<b>시간대</b>와 <b>카테고리</b>를 편집하세요!\n"
                    "설정을 하지 않으면 뉴스가 발송되지 않아요.🤐\n",
                    reply_markup={
                        "inline_keyboard": [[
                            {"text": "⚙️ 설정하러 가기", "url": encrypted_link}
                        ]]
                    }
                )
            else:
                existing["subscribed"] = True
                existing["first_name"] = first_name
                existing["last_name"] = last_name
                existing["username"] = username
                save_recipients_telegram(recipients)
                send_message(
                    chat_id,
                    "✅ <b>구독을 다시 시작했습니다.</b>\n\n"
                    "링크를 눌러 <b>시간대</b>와 <b>카테고리</b>를 편집하세요!\n"
                    "설정을 하지 않으면 뉴스가 발송되지 않아요.🤐\n",
                    reply_markup={
                        "inline_keyboard": [[
                            {"text": "⚙️ 설정하러 가기", "url": encrypted_link}
                        ]]
                    }
                )
        else:
            recipients.append({
                "chat_id": chat_id,
                "subscribed": True,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "subscribed_at": datetime.now().isoformat()  # ISO 형식 문자열로 저장
            })
            save_recipients_telegram(recipients)
            

            send_message(
                chat_id,
                "👋 안녕하세요! AI뉴스 요약 봇입니다.\n\n"
                "링크를 눌러 <b>시간대</b>와 <b>카테고리</b>를 선택하세요!\n"
                "설정을 하지 않으면 뉴스가 발송되지 않아요.🤐\n",
                reply_markup={
                    "inline_keyboard": [[
                        {"text": "⚙️ 설정하러 가기", "url": encrypted_link}
                    ]]
                }
            )

    elif text == "/stop":
        for r in recipients:
            if r["chat_id"] == chat_id:
                r["subscribed"] = False
        save_recipients_telegram(recipients)
        send_message(chat_id, "⛔️ 뉴스 구독이 해제되었습니다.")

    elif text == "/help":
        help_message = (
            "🆘 <b>도움말</b>\n\n"
            "/start - 뉴스 구독 시작\n"
            "/stop - 뉴스 구독 중지\n"
            "/setting - 뉴스레터 수신 설정\n"
            "/help - 이 메시지 보기\n\n"
            "👇 이메일로도 뉴스레터를 받을 수 있어요! 👇"
        )

        send_message(
            chat_id,
            help_message,
            parse_mode="HTML",
            reply_markup={
                "inline_keyboard": [[
                    {"text": "✉️ 이메일 구독하기", "url": "https://leeyoungjun.duckdns.org/news-bot?subscribe"}
                ]]
            }
        )

    elif text == "/setting":

        message = (
        "📰 <b>뉴스레터 설정 페이지</b>\n\n"
        "원하는 시간대와 카테고리를 선택할 수 있어요.\n"
        "아래 버튼을 눌러 바로 설정하세요 👇"
        )

        reply_markup = {
            "inline_keyboard": [[
                {"text": "⚙️ 설정하러 가기", "url": encrypted_link}
            ]]
        }

        send_message(chat_id, message, parse_mode="HTML", reply_markup=reply_markup)

    return "OK"

# 뉴스 설정 페이지 리다이렉트 (프론트엔드 라우팅으로 대체)
# 이 라우트는 React 앱의 /preferences 경로로 리다이렉트해야 합니다.
@app.route("/news-settings")
def settings():
    token = request.args.get("token", "").strip()

    if not token:
        return "Missing token", 400 # JSON 응답으로 변경 고려

    result = decode_token_safe(token)

    if "error" in result:
        # 에러 발생 시 JSON 응답으로 변경 고려
        return result["error"], 400

    payload = result["payload"]
    email = payload.get("email")
    chat_id = payload.get("chat_id")

    if not email and not chat_id:
        return "Invalid token (missing email/chat_id)", 400 # JSON 응답으로 변경 고려

    # React 앱의 /preferences 경로로 리다이렉트. 
    # Flask는 단순히 리다이렉션만 수행하고, React 앱이 나머지 데이터 로딩을 처리합니다.
    # NEWSLETTER_URL이 React 앱의 기본 URL을 가리켜야 합니다.
    # 예: NEWSLETTER_URL = "http://localhost:3000" (개발 시) 또는 "https://yourdomain.com" (배포 시)
    query = urlencode({"token": result["token"]})
    return redirect(f"{NEWSLETTER_URL}/preferences?{query}")
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3200, debug=True)
    app.url_map.strict_slashes = False