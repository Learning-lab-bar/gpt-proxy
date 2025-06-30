import os
import openai
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS

# אתחול Flask
app = Flask(__name__)
CORS(app)

# קובץ מפתח של Firebase (שמרת אותו קודם)
cred = credentials.Certificate("serviceAccountKey.json")  # ודאי שהוא בקובץ זהה לשם
firebase_admin.initialize_app(cred)
db = firestore.client()

# הגדרת הנתיב לשיחה
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        participant_id = data.get("participantId", "unknown")

        # שליחת הודעה ל־OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = response.choices[0].message["content"]

        # שמירת ההודעה במסד הנתונים Firestore
        doc_ref = db.collection("chat_logs").document(participant_id)
        doc_ref.set({
            "participantId": participant_id,
            "chatLog": messages + [{"role": "assistant", "content": reply}],
        }, merge=True)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
