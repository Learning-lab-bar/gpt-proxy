from flask import Flask, request, Response
from flask_cors import CORS
import openai, os, json, traceback

app = Flask(__name__)

# פתרון CORS מלא שמאפשר גם preflight
CORS(app, origins="*", allow_headers="*", methods=["POST", "OPTIONS"])

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        # תשובה ל־preflight
        return Response(status=204)

    try:
        data = request.json
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=data.get("messages", [])
        )
        reply = response.choices[0].message.content.strip('"')
        payload = json.dumps({"reply": reply}, ensure_ascii=False)
        return Response(payload, mimetype="application/json")

    except Exception as e:
        traceback.print_exc()
        error_msg = json.dumps({"error": str(e)}, ensure_ascii=False)
        return Response(error_msg, status=500, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
