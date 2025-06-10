from flask import Flask, request, Response
from flask_cors import CORS
import openai
import os
import json
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
        reply = raw_reply.strip('"')

        # שימוש ב-ensure_ascii=False כדי לא להמיר עברית ל-\u05e9
        payload = json.dumps({"reply": reply}, ensure_ascii=False)
        return Response(payload, mimetype="application/json")

    except Exception as e:
        traceback.print_exc()
        error_msg = json.dumps({"error": str(e)}, ensure_ascii=False)
        return Response(error_msg, status=500, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
