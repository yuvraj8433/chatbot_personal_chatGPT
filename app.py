import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()


# ====== PUT YOUR KEYS HERE ======
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")



MODEL = "mistralai/mistral-7b-instruct"

app = Flask(__name__)

# ---------- MEMORY ----------
os.makedirs("memory", exist_ok=True)

def load_memory(user_id):
    path = f"memory/{user_id}.json"
    if os.path.exists(path):
        return json.load(open(path, "r", encoding="utf-8"))

    return [{"role":"system","content":"You are a helpful AI assistant."}]

def save_memory(user_id, messages):
    json.dump(messages, open(f"memory/{user_id}.json","w"), indent=2)

# ---------- AI FUNCTION ----------
def ask_ai(user_id, text):
    messages = load_memory(user_id)
    messages.append({"role":"user","content":text})

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nexa-ai.onrender.com",
            "X-Title": "NexaAI"
        },
        json={
            "model": MODEL,
            "messages": messages
        }
    )

    result = response.json()
    reply = result["choices"][0]["message"]["content"]

    messages.append({"role":"assistant","content":reply})
    save_memory(user_id, messages)

    return reply

# ---------- WEBSITE API ----------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    reply = ask_ai(data["user_id"], data["message"])
    return jsonify({"reply": reply})

# ---------- TELEGRAM WEBHOOK ----------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram():
    data = request.get_json()

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text","")

    reply = ask_ai(str(chat_id), text)

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )

    return "ok"

@app.route("/")
def home():
    return "Nexa AI Running"
