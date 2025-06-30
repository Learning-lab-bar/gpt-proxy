from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import openai
import os

app = Flask(__name__)
CORS(app)

# הגדרת לקוח OpenAI (API Key מהסביבה)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# כתובת Google Apps Script שלך לשמירת השיחה
GAS_URL = "https://script.google.com/macros/s/AKfycbyvJ8ZNLPqKn6zCNeuVuNrTXJRX7J5OehJWZxdOjVpgVEVXareVEJQBTf4KyWEdFBSaow/exec"

@app.route("/")
def home():
    return f"✅ GPT Proxy is running using model: {OPENAI_MODEL}"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

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
