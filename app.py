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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=data.get("messages", [])
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
