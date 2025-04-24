from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

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

@app.route("/subscribe.html")
def serve_subscribe():
    return send_from_directory(".", "subscribe.html")

@app.route("/unsubscribe.html")
def serve_unsubscribe():
    return send_from_directory(".", "unsubscribe.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "이름과 이메일은 필수입니다."}), 400

    recipients = load_recipients()
    if any(r["email"] == email for r in recipients):
        return jsonify({"message": "이미 구독 중입니다."}), 200

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recipients.append({"name": name, "email": email, "subscribed_at": timestamp})
    save_recipients(recipients)
    return jsonify({"message": "구독이 완료되었습니다."}), 200

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

@app.route("/")
def index():
    return "<h2>👋 안녕하세요! 원하시는 서비스를 선택하세요!</h2><p><a href='/subscribe.html'>구독 신청</a> | <a href='/unsubscribe.html'>구독 해제</a></p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
