
import os, requests
from dotenv import load_dotenv

def send_alert(bot_name, msg):
    try:
        load_dotenv()
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID', '277954993')
        txt = f"🤖 {bot_name}\n{msg}"
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', 
                      json={'chat_id': chat_id, 'text': txt})
    except Exception:
        pass
