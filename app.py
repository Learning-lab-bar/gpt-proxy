from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime

app = Flask(__name__)
CORS(app)

# התחברות ל־OpenAI API
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
model_name = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# אתחול Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ---------- נתיב לשיחות GPT ----------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        participant_id = data.get("participantId", "unknown")
        user_messages = data.get("messages", [])

        if not user_messages:
            return jsonify({"error": "No user message provided"}), 400

        user_message = user_messages[-1]

        # שליפת שיחה קודמת
        doc_ref = db.collection("chat_logs").document(participant_id)
        doc = doc_ref.get()
        previous_messages = doc.to_dict().get("messages", []) if doc.exists else []

        full_conversation = previous_messages + [user_message]

        # שליחה ל־GPT
        response = client.chat.completions.create(
            model=model_name,
            messages=full_conversation
        )

        reply = response.choices[0].message.content

        # יצירת רשומות עם timestamp לכל הודעה
        timestamp = datetime.datetime.utcnow().isoformat()
        new_entries = [
            {
                "role": user_message["role"],
                "content": user_message["content"],
                "timestamp": timestamp
            },
            {
                "role": "assistant",
                "content": reply,
                "timestamp": timestamp
            }
        ]

        # עדכון/יצירת מסמך
        doc_ref.set({
            "participantId": participant_id,
            "lastUpdated": timestamp
        }, merge=True)

        doc_ref.update({
            "messages": firestore.ArrayUnion(new_entries)
        })

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- נתיב לשמירת מעקב טאבים ----------
@app.route("/save-memory", methods=["POST"])
def save_memory():
    try:
        data = request.get_json()
        response_id = data.get("responseId")
        total_hidden_time = data.get("totalHiddenTime")
        tab_log = data.get("TabVisibilityLog")  # מגיע מה-JavaScript

        if not response_id:
            return jsonify({"error": "Missing responseId"}), 400

        doc_ref = db.collection("memory_logs").document(response_id)

        doc_ref.set({
            "TotalHiddenTime": total_hidden_time,
            "TabVisibilityLog": firestore.ArrayUnion(tab_log or [])
        }, merge=True)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# הרצת השרת
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
