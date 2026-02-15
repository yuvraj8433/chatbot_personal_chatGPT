import os
import json
import requests
from flask import Flask, request, jsonify

API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"

MEMORY_FOLDER = "memory"
os.makedirs(MEMORY_FOLDER, exist_ok=True)

app = Flask(__name__)

# -------- MEMORY ----------
def memory_path(user_id):
    return f"{MEMORY_FOLDER}/{user_id}.json"

def load_memory(user_id):
    path = memory_path(user_id)
    if os.path.exists(path):
        return json.load(open(path, "r", encoding="utf-8"))

    return [{
        "role": "system",
        "content": "You are a helpful AI assistant. Give short professional answers."
    }]

def save_memory(user_id, messages):
    json.dump(messages, open(memory_path(user_id), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# -------- AI CHAT ----------
def ask_ai(user_id, text):
    messages = load_memory(user_id)
    messages.append({"role": "user", "content": text})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://nexa-ai.onrender.com",  # required
                "X-Title": "Nexa AI"  # required
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 800
            }
        )

        print("OpenRouter raw:", response.text)  # debug log

        result = response.json()
        reply = result["choices"][0]["message"]["content"]

    except Exception as e:
        print("OPENROUTER ERROR:", e)
        reply = "AI server error. Please try again."

    messages.append({"role": "assistant", "content": reply})
    save_memory(user_id, messages)

    return reply


# -------- API ROUTE ----------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data["user_id"]
    message = data["message"]

    reply = ask_ai(user_id, message)
    return jsonify({"reply": reply})

@app.route("/")
def home():
    return "Nexa AI Running"

if __name__ == "__main__":
    app.run()

from telegram_bot import telegram_webhook
telegram_webhook(app)
