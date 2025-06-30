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

# אתחול Firebase עם קובץ השירות מה־Secrets של Render
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

        # קריאת מסמך קיים (אם קיים) כדי לשמור את ההיסטוריה
        doc_ref = db.collection("chat_logs").document(participant_id)
        doc = doc_ref.get()

        if doc.exists:
            previous_log = doc.to_dict().get("log", [])
        else:
            previous_log = []

        # הוספת ההודעה הנוכחית להיסטוריה
        new_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "messages": messages,
            "reply": reply
        }

        updated_log = previous_log + [new_entry]

        # עדכון המסמך עם היסטוריית השיחה המצטברת
        doc_ref.set({
            "participantId": participant_id,
            "log": updated_log
        }, merge=True)

        return jsonify({"reply": reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# הפעלת השרת
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
