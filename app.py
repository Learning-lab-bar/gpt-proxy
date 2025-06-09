from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# קריאת מפתח ה-API מהסביבה
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    try:
        # הדפסת הנתונים שהתקבלו לצורך דיבוג
        print("📥 Received data:", data)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=data.get("messages", [])
        )

        reply = response.choices[0].message.content
        print("📤 GPT reply:", reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
