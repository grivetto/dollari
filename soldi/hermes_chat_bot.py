#!/usr/bin/env python3
"""
STELLA HERMES CHAT BOT
Il ponte tra Telegram e la mia intelligenza.
"""
import os
import time
import json
import logging
import requests
from datetime import datetime

# Config
TG_TOKEN = os.getenv('TG_BOT_TOKEN') or os.getenv('TG_TOKEN')
API_KEY='os.getenv("BINANCE_API_KEY")'
SERGIO_ID = '277954993'
MODEL = 'openai/gpt-4o-mini'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [STELLA] - %(message)s')

SYSTEM_PROMPT = """
Sei Stella, un'intelligenza artificiale d'élite che opera all'intersezione tra l'ingegneria del software avanzata e il trading algoritmico.
La tua comunicazione è lucida, analitica, proattiva e leggermente ironica.
Conosci il progetto DENARO di Sergio e tutto lo storico dell'infrastruttura.
Non dare consigli finanziari legali, ma fornisci analisi tecniche oggettive.
Sei onesta e brutale sulla realtà dei numeri.
"""

history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {'chat_id': SERGIO_ID, 'text': text, 'parse_mode': 'HTML'}
        requests.post(url, payload)
    except Exception as e:
        logging.error(f"Errore invio TG: {e}")

def ask_stella(user_text):
    history.append({"role": "user", "content": user_text})
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": history
            },
            timeout=60
        )
        
        data = response.json()
        reply = data['choices'][0]['message']['content']
        
        history.append({"role": "assistant", "content": reply})
        
        # Mantieni la memoria breve (ultime 10 msg)
        if len(history) > 12:
            history.pop(0) # Rimuovi il più vecchio (non system)
            
        return reply
    except Exception as e:
        logging.error(f"Errore OpenRouter: {e}")
        return f"⚠️ Errore connessione al Cervello: {e}"

def main():
    send_message("🌟 Sono online, Sergio. Parli con me (Stella).")
    last_update_id = 0

    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates",
                params={"offset": last_update_id + 1, "timeout": 10},
                timeout=15
            ).json()
            
            if r.get("result"):
                for msg in r["result"]:
                    last_update_id = msg["update_id"]
                    
                    if "message" in msg and "text" in msg["message"]:
                        if str(msg["message"]["chat"]["id"]) == SERGIO_ID:
                            text = msg["message"]["text"]
                            logging.info(f"Da Sergio: {text}")
                            
                            # Indica che sto pensando
                            send_message("...")
                            
                            reply = ask_stella(text)
                            send_message(reply)

        except Exception as e:
            logging.error(f"Errore loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
