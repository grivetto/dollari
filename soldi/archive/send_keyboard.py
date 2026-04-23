import os
from dotenv import load_dotenv
load_dotenv("/home/sergio/.openclaw/workspace/denaro/.env.telegram")
import requests
import json

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "277954993"
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

keyboard = {
    "keyboard": [
        [{"text": "/status"}, {"text": "/history"}],
        [{"text": "/help"}, {"text": "/memory"}],
        [{"text": "/stop"}, {"text": "/ping"}]
    ],
    "resize_keyboard": True,
    "persistent": True
}

data = {
    "chat_id": CHAT_ID,
    "text": "Hai chiesto un menù per controllare me (sergio_bot)? Eccolo! ⭐\n\nHo inserito i comandi principali per interagire con OpenClaw. Clicca sui tasti qui sotto in qualsiasi momento per farmi fare un check del sistema o controllare i miei ricordi.",
    "reply_markup": json.dumps(keyboard)
}

requests.post(URL, json=data)
