from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime

app = Flask(__name__)
CORS(app)

# אתחול לקוח OpenAI עם מפתח מהסביבה
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# אתחול Firebase עם קובץ השירות מה־Secret File (Render)
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

        # שליחת ההודעה ל־GPT (גרסה עדכנית)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message.content

        # שמירת השיחה למסד הנתונים
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

# פתיחת השרת בפורט הנדרש עבור Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
