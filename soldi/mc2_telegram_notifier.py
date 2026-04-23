#!/usr/bin/env python3
"""
MC2 TELEGRAM NOTIFIER — Inoltra alert a @Sergio1969bot
Monitora il log del Rebound Sniper e invia notifiche per:
- Segnali RSI < 35 (ipervenduto = opportunità acquisto)
- Trade eseguiti
- Errori critici
"""
import requests
import time
import os

TG_TOKEN = 'os.getenv("TELEGRAM_TOKEN")'
TG_CHAT = '277954993'
LOG_FILE = '/home/sergio/denaro/logs/rebound_sniper.log'

last_pos = 0
seen_signals = set()

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, json={'chat_id': TG_CHAT, 'text': msg, 'parse_mode': 'HTML'}, timeout=10)
    except: pass

def tail_log():
    global last_pos
    try:
        with open(LOG_FILE, 'r') as f:
            f.seek(last_pos)
            new = f.read()
            last_pos = f.tell()
            return new
    except: return ""

def check_log(text):
    for line in text.split("\n"):
        if not line.strip(): continue
        if "RSI:" in line:
            # Cerca coppie con RSI basso
            for pair in ["ETH/BTC", "SOL/BTC", "BNB/BTC", "LINK/BTC", "AVAX/BTC"]:
                if pair in line:
                    parts = line.split("—")
                    if len(parts) >= 2:
                        rsi_part = parts[-1]
                        try:
                            rsi_val = float(rsi_part.split("RSI:")[1].split("|")[0].strip())
                            if rsi_val < 35 and pair+line[:10] not in seen_signals:
                                seen_signals.add(pair+line[:10])
                                msg = "🎯 <b>MC2 SNIPER ALERT</b>\n"
                                msg += f"📉 {pair} RSI: {rsi_val:.1f}\n"
                                msg += "⚡ Zona ipervenduta — Possibile opportunità"
                                send(msg)
                        except: pass

        if "ERRORE" in line or "CRITICAL" in line:
            msg = f"🚨 <b>MC2 ERRORE</b>\n<pre>{line[:200]}</pre>"
            send(msg)

print("🤖 MC2 Telegram Notifier avviato")
send("✅ <b>MC2 Notifier ONLINE</b>\nMonitoraggio Rebound Sniper attivo\nTi avviso quando RSI < 35")

while True:
    new_text = tail_log()
    if new_text:
        check_log(new_text)
    time.sleep(5)
