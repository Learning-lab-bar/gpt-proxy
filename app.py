from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    try:
        print("📥 Got data:", data, flush=True)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=data.get("messages", [])
        )

        reply = response.choices[0].message.content
        print("📤 GPT reply:", reply, flush=True)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
