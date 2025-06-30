from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime

# אתחול Flask
app = Flask(__name__)
CORS(app)

# התחברות ל־OpenAI API החדש
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
model_name = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# אתחול Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        participant_id = data.get("participantId", "unknown")
        user_messages = data.get("messages", [])

        # שליפת השיחה המצטברת ממסד הנתונים
        doc_ref = db.collection("chat_logs").document(participant_id)
        doc = doc_ref.get()

        full_messages = []
        if doc.exists:
            full_messages = doc.to_dict().get("messages", [])

        # הוספת ההודעה החדשה לרשימת ההודעות
        full_messages.extend(user_messages)

        # קריאה ל־OpenAI
        response = client.chat.completions.create(
            model=model_name,
            messages=full_messages
        )

        reply = response.choices[0].message.content

        # הוספת התשובה להיסטוריית השיחה
        full_messages.append({
            "role": "assistant",
            "content": reply
        })

        # עדכון / יצירת המסמך במסד הנתונים
        doc_ref.set({
            "participantId": participant_id,
            "messages": full_messages,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# הרצת השרת
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
