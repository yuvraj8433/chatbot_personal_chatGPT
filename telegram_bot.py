import os
import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ====== KEYS ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct"

MEMORY_FOLDER = "memory"
os.makedirs(MEMORY_FOLDER, exist_ok=True)


# ---------- MEMORY FUNCTIONS ----------
def get_memory_path(user_id):
    return f"{MEMORY_FOLDER}/{user_id}.json"


def load_memory(user_id):
    path = get_memory_path(user_id)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # first message system prompt
    return [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Give short, clean, professional answers."
        }
    ]


def save_memory(user_id, messages):
    with open(get_memory_path(user_id), "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


# ---------- OPENROUTER CHAT ----------
def chat_with_ai(user_id, user_text):
    messages = load_memory(user_id)

    messages.append({"role": "user", "content": user_text})

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2,
        "top_p": 0.8,
        "max_tokens": 800
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    ai_reply = result["choices"][0]["message"]["content"].strip()

    messages.append({"role": "assistant", "content": ai_reply})
    save_memory(user_id, messages)

    return ai_reply


# ---------- TELEGRAM COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nexa AI Bot ready. Send me a message.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_text = update.message.text

    # await update.message.reply_text("Thinking...")

    reply = chat_with_ai(user_id, user_text)

    await update.message.reply_text(reply)


# ---------- RUN BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Telegram Bot Running...")
app.run_polling()
