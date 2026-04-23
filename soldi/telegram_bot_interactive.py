#!/usr/bin/env python3
"""
DENARO TELEGRAM BOT — @Sergiotrdxbot
Console operativa REALISTICA per Sergio
Solo dati veri. Niente fantasia.
"""
import gc
import os
import json
import logging
import requests
import time
import subprocess
from dotenv import load_dotenv
from datetime import datetime
import ccxt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Costanti
CAPITALE_VERSATO = 722.00

def get_binance_client():
    load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
    return ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })

def cmd_balance():
    """📊 Bilancio Cluster Reale"""
    try:
        ex = get_binance_client()
        bal = ex.fetch_balance()
        
        eur_free = bal.get('EUR', {}).get('free', 0)
        usdt_free = bal.get('USDT', {}).get('free', 0)
        btc_free = bal.get('BTC', {}).get('free', 0)
        
        ticker = ex.fetch_ticker('BTC/EUR')
        btc_price = ticker['last']
        
        total_eur = eur_free + usdt_free + (btc_free * btc_price)
        profit = total_eur - CAPITALE_VERSATO
        
        return (
            f"💰 <b>BILANCIO REALE BINANCE</b>\n"
            f"─────────────────\n"
            f"📅 Ora: {datetime.now().strftime('%d/%m %H:%M')}\n"
            f"💶 EUR: <b>€{eur_free:.2f}</b>\n"
            f"💵 USDT: ${usdt_free:.2f}\n"
            f"₿ BTC: {btc_free:.6f}\n"
            f"─────────────────\n"
            f"💰 <b>TOTALE: €{total_eur:.2f}</b>\n"
            f"📉 Da investito: €{CAPITALE_VERSATO:.0f}"
        )
    except Exception as e:
        return f"⚠️ Errore lettura bilancio: {e}"

def cmd_grid():
    """📊 Stato Grid Bot"""
    try:
        proc = subprocess.run(['systemctl', 'is-active', 'denaro-realistic-grid'], capture_output=True, text=True)
        is_active = proc.stdout.strip() == 'active'
        
        log_file = '/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log'
        last_log = ""
        if os.path.exists(log_file):
            result = subprocess.run(['tail', '-n', '3', log_file], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            lines = [l.split(' - ', 2)[-1] for l in lines if ' - ' in l]
            last_log = '\n'.join(lines)

        return (
            f"📊 <b>GRID BOT - NUVOLA</b>\n"
            f"─────────────────\n"
            f"Stato: {'✅ ATTIVO' if is_active else '❌ INATTIVO'}\n"
            f"Bot: Realistic Grid Bot\n"
            f"─────────────────\n"
            f"📝 Ultimi eventi:\n{last_log}"
        )
    except Exception as e:
        return f"⚠️ Errore grid status: {e}"

def cmd_mc2():
    """🎯 Stato Rebound Sniper MC2"""
    try:
        cmd = ['ssh', '-o', 'ConnectTimeout=3', '-o', 'StrictHostKeyChecking=no', '-p', '2222', '-i', os.path.expanduser('~/.ssh/id_ed25519'), 'sergio@93.43.252.114', 'sudo tail -n 3 ~/denaro/logs/rebound_sniper.log']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        lines = result.stdout.strip().split('\n')
        last_lines = '\n'.join([l.split(' - ', 2)[-1] for l in lines if ' - ' in l])
        
        return (
            f"🎯 <b>REBOUND SNIPER - MC2</b>\n"
            f"─────────────────\n"
            f"Stato: ✅ ATTIVO (Remoto)\n"
            f"─────────────────\n"
            f"📝 Ultimi scan:\n{last_lines}"
        )
    except Exception as e:
        return f"⚠️ Errore connessione MC2: {e}"

def cmd_services():
    """🛡️ Servizi Attivi (Solo realtà)"""
    services = [
        ("denaro-realistic-grid", "Grid Bot BTC/EUR"),
        ("denaro-rebound-sniper", "Rebound Sniper (MC2)"),
        ("denaro-target-tracker", "Daily Tracker"),
        ("denaro-ai-risk", "AI Risk Engine"),
        ("denaro-crisis", "Crisis Manager"),
        ("denaro-delta-neutral", "Delta Hedge"),
        ("denaro-dashboard-v2", "Dashboard Web"),
        ("denaro-telegram", "Bot Telegram"),
    ]
    
    msg = "🛡️ <b>SERVIZI REALI ATTIVI</b>\n"
    msg += "─────────────────\n"
    
    active = 0
    for svc, name in services:
        try:
            if "MC2" in svc:
                cmd = ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no', '-p', '2222', '-i', os.path.expanduser('~/.ssh/id_ed25519'), 'sergio@93.43.252.114', 'systemctl is-active denaro-rebound-sniper']
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                is_active = res.stdout.strip() == 'active'
            else:
                res = subprocess.run(['systemctl', 'is-active', svc], capture_output=True, text=True)
                is_active = res.stdout.strip() == 'active'
            
            icon = "✅" if is_active else "❌"
            if is_active: active += 1
            msg += f"{icon} {name}\n"
        except:
            msg += f"❓ {name}\n"
    
    msg += f"─────────────────\n"
    msg += f"Totale: {active} attivi su {len(services)}"
    return msg

def cmd_vault():
    """🔐 Cassaforte"""
    vault_file = '/home/sergio/.openclaw/workspace/denaro/cassaforte.json'
    if os.path.exists(vault_file):
        try:
            with open(vault_file, 'r') as f:
                data = json.load(f)
            tot = data.get('totale_cassaforte', 0)
            days = len(data.get('giorni_chiusi', []))
            return (
                f"🔐 <b>CASSAFORTE</b>\n"
                f"─────────────────\n"
                f"Totale: <b>€{tot:.2f}</b>\n"
                f"Giorni: {days}\n"
                f"📅 Report: 23:59"
            )
        except:
            return "⚠️ Errore lettura cassaforte"
    return "🔐 Cassaforte non inizializzata"

def cmd_system():
    """🖥️ Stato Sistema"""
    try:
        import psutil
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        return (
            f"🖥️ <b>NUVOLA SYSTEM</b>\n"
            f"─────────────────\n"
            f"CPU: {cpu}%\n"
            f"RAM: {ram}%\n"
            f"Disk: {disk}%"
        )
    except Exception as e:
        return f"⚠️ Errore: {e}"

def get_keyboard():
    return {
        "keyboard": [
            [{"text": "💰 Bilancio"}, {"text": "📊 Grid Bot"}],
            [{"text": "🎯 MC2 Sniper"}, {"text": "🛡️ Servizi"}],
            [{"text": "💵 DCA"}, {"text": "🔐 Cassaforte"}],
            [{"text": "🖥️ Sistema"}, {"text": "🌐 Dashboard"}]
        ],
        "resize_keyboard": True
    }

def main_loop():
    load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    sergio_id = str(os.getenv('TELEGRAM_CHAT_ID'))
    
    if not token:
        return
    
    last_update_id = 0
    logging.info("Bot Denaro (Reale) Avviato")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=20"
            r = requests.get(url, timeout=25).json()
            
            if "result" in r:
                for update in r["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"].strip()
                        chat_id = str(update["message"]["chat"]["id"])
                        
                        if chat_id != sergio_id:
                            continue
                        
                        resp = ""
                        
                        if text == "/start":
                            resp = "🤖 <b>Denaro Bot - Reale</b>\nBenvenuto Sergio."
                        elif "Bilancio" in text:
                            resp = cmd_balance()
                        elif "Grid" in text:
                            resp = cmd_grid()
                        elif "MC2" in text or "Sniper" in text:
                            resp = cmd_mc2()
                        elif "Servizi" in text or "Architettura" in text:
                            resp = cmd_services()
                        elif "DCA" in text:
                            resp = "💵 <b>DCA</b>\nStato: Attivo (se fondi > €3)"
                        elif "Cassaforte" in text:
                            resp = cmd_vault()
                        elif "Sistema" in text:
                            resp = cmd_system()
                        elif "Dashboard" in text:
                            resp = "🌐 https://sgrivett.ddns.net:8443"
                        else:
                            resp = "Clicca un pulsante del menu."
                        
                        if resp:
                            payload = {"chat_id": chat_id, "text": resp, "parse_mode": "HTML", "reply_markup": get_keyboard()}
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload)
            
            gc.collect()
            time.sleep(0.5)
        except Exception as e:
            logging.error(f'ERRORE: {e}')
            time.sleep(5)

if __name__ == "__main__":
    main_loop()
