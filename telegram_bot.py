import requests
from flask import request

BOT_TOKEN = "8408768188:AAEnk3LUMsOSnXd-RADXvzn-K6TcPlYrBeE"
BACKEND_URL = "https://your-render-url.onrender.com/chat"

def telegram_webhook(app):

    @app.route(f"/{BOT_TOKEN}", methods=["POST"])
    def telegram():
        data = request.get_json()

        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text","")

        payload = {
            "user_id": str(chat_id),
            "message": text
        }

        reply = requests.post(BACKEND_URL, json=payload).json()["reply"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

        return "ok"
