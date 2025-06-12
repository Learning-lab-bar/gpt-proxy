from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# כתובת Google Apps Script שלך
GAS_URL = "https://script.google.com/macros/s/AKfycbyvJ8ZNLPqKn6zCNeuVuNrTXJRX7J5OehJWZxdOjVpgVEVXareVEJQBTf4KyWEdFBSaow/exec"

@app.route("/")
def home():
    return "✅ GPT Proxy is running."

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # שליחה ל־OpenAI דרך קוד שכבר קיים אצלך
        # כאן זה רק placeholder
        return jsonify({"reply": "🔧 אין מודל מוגדר כאן. בדקי את קוד ה־chat שלך."})
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
    app.run()
