from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import traceback

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    print("📥 Got data:", data, flush=True)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=data.get("messages", [])
        )

        raw_reply = response.choices[0].message.content
        print("🧾 Raw reply from GPT:", repr(raw_reply), flush=True)

        # הסרת גרשיים מיותרים אם יש
        reply = raw_reply.strip('"')
        print("✅ Cleaned reply:", reply, flush=True)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error:", str(e), flush=True)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
