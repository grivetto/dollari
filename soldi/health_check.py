#!/usr/bin/env python3
"""
HEALTH CHECK — Verifica bot ogni 15 minuti
Invia alert Telegram se qualcosa è rotto
"""

import os
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID', '277954993')

# Servizi per nodo
SERVICES_NUVOLA = [
    'denaro-realistic-grid',
    'denaro-target-tracker'
]

SERVICES_MC2 = [
    'denaro-rebound-sniper'
]

def send_alert(message):
    """Invia alert Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        payload = {'chat_id': TG_CHAT, 'text': message, 'parse_mode': 'HTML'}
        requests.post(url, payload, timeout=10)
    except:
        pass

def check_service(name):
    """Verifica se servizio systemd è attivo"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def check_api():
    """Verifica connessione API Binance"""
    try:
        import ccxt
        ex = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
        })
        ex.fetch_balance()
        return True
    except:
        return False

def main():
    errors = []
    
    # Check servizi
    for svc in SERVICES:
        if not check_service(svc):
            errors.append(f"❌ {svc} DOWN")
    
    # Check API
    if not check_api():
        errors.append("❌ API Binance ERROR")
    
    # Check spazio disco
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        usage = lines[1].split()[4].replace('%', '')
        if int(usage) > 90:
            errors.append(f"⚠️ Disk {usage}% full")
    except:
        pass
    
    # Check RAM
    try:
        result = subprocess.run(['free'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        mem_line = lines[1].split()
        used = int(mem_line[2])
        total = int(mem_line[1])
        pct = (used / total) * 100
        if pct > 95:
            errors.append(f"⚠️ RAM {pct:.0f}% full")
    except:
        pass
    
    if errors:
        msg = f"🚨 <b>HEALTH CHECK ALERT</b>\n<b>Ora:</b> {datetime.now().strftime('%H:%M')}\n\n" + "\n".join(errors)
        send_alert(msg)
        print(f"ALERT: {msg}")
    else:
        print(f"✅ {datetime.now().strftime('%H:%M')} — Tutto OK")

if __name__ == "__main__":
    main()
