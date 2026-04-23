import os
import requests
import sys

# Aggiungi la cartella corrente al path per importare telegram_bot_interactive
sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro/')
import telegram_bot_interactive as tbi
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env.telegram')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


from datetime import datetime
import pytz

def main():
    now = datetime.now(pytz.timezone('Europe/Rome'))
    if 0 <= now.hour < 6:
        print("Orario notturno (00:00 - 06:00). Notifiche disabilitate.")
        return

    status_text = tbi.get_full_status()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"⏱️ *REPORT ORARIO AUTOMATICO*\n{status_text}", "parse_mode": "Markdown"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    main()
