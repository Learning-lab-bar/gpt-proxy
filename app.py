from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime

app = Flask(__name__)
CORS(app)

# הגדרת מפתח OpenAI דרך משתנה סביבה
openai.api_key = os.environ.get("OPENAI_API_KEY")

# אתחול Firebase עם קובץ השירות מה־Secret File
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        participant_id = data.get("participantId", "unknown")

        # שליחת ההודעה ל־GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message["content"]

        # שמירת השיחה במסד הנתונים
        log_entry = {
            "participantId": participant_id,
            "messages": messages,
            "reply": reply,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        db.collection("chat_logs").add(log_entry)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
