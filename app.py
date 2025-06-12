from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # מאפשר בקשות ממקורות חיצוניים (כמו GitHub Pages)

# כתובת Google Apps Script שלך לשמירה
GAS_URL = "https://script.google.com/macros/s/AKfycbyvJ8ZNLPqKn6zCNeuVuNrTXJRX7J5OehJWZxdOjVpgVEVXareVEJQBTf4KyWEdFBSaow/exec"

@app.route("/")
def home():
    return "✅ GPT Proxy is running."

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])

        # כאן יש לקרוא ל־OpenAI GPT אם תרצי (מושמט כרגע)
        # זו תגובת דמה
        last_user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "שאלה?")
        dummy_reply = f"זו תשובה דמה ל: {last_user_msg}"

        return jsonify({"reply": dummy_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/save-chat", methods=["POST"])
def save_chat():
    try:
        response = requests.post(GAS_URL, json=request.json)
        return response.text, response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

