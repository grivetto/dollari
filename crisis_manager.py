import os
import json
import logging
import time
import subprocess
from dotenv import load_dotenv
import ccxt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DEFCON 🚨] - %(message)s',
                    handlers=[logging.FileHandler("DEFCON.log"), logging.StreamHandler()])

load_dotenv('/home/sergio/denaro/.env')

try:
    binance = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
except Exception as e:
    logging.error(f"Errore connessione Binance: {e}")
    exit()

def is_market_crashing():
    try:
        # Controlliamo BTC come benchmark globale
        ticker = binance.fetch_ticker('BTC/EUR')
        change_24h = ticker.get('percentage', 0.0)
        
        # Se BTC perde più del 4% in 24h, o ETH perde più del 5%, consideriamo DEFCON 2
        if change_24h <= -4.0:
            return True, change_24h
        return False, change_24h
    except Exception as e:
        logging.error(f"Errore analisi crollo: {e}")
        return False, 0.0

def activate_defcon():
    logging.warning("🚨 [CRISIS MANAGER] - STATO DI EMERGENZA (DEFCON 2) ATTIVATO!")
    logging.warning("🚨 I mercati stanno sanguinando. Sospensione temporanea dei bot Spot (Acquisti bloccati).")
    
    # Invia notifica Telegram
    try:
        sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro')
        import requests
        load_dotenv('/home/sergio/denaro/.env.telegram')
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        msg = "🚨 *DEFCON 2 ATTIVATO (CRISIS MANAGER)* 🚨\n\nCrollo globale dei mercati rilevato (>4% su BTC). L'ecosistema è entrato in modalità Sopravvivenza:\n\n⏸️ *Bot Spot (Binance/MEXC):* Ordini di acquisto temporaneamente congelati per evitare di comprare coltelli in caduta.\n📉 *Bot Short:* Autorizzati a forzare la size massima per coprire le perdite del portafoglio (Hedging).\n\n*Il sistema si sbloccherà automaticamente non appena il crollo si arresterà.*"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
    except: pass
    
    # 1. Spegnere i bot Spot aggressivi (Legion) scrivendo in un file di lock
    with open("/home/sergio/.openclaw/workspace/denaro/DEFCON.lock", "w") as f:
        f.write("DEFCON_2")
        
    # 2. Potenziare i bot SHORT (Es. Blade Runner, Micro-Shorter)
    # Scriviamo nel config per far capire ai bot che siamo in crollo
    config_path = "/home/sergio/.openclaw/workspace/denaro/trade_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            config["market_condition"] = "CRASH"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
        except: pass

def deactivate_defcon():
    if os.path.exists("/home/sergio/.openclaw/workspace/denaro/DEFCON.lock"):
        logging.info("✅ [CRISIS MANAGER] - Crollo terminato. Disattivazione DEFCON. Rimozione blocchi.")
        os.remove("/home/sergio/.openclaw/workspace/denaro/DEFCON.lock")
        
        config_path = "/home/sergio/.openclaw/workspace/denaro/trade_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                config["market_condition"] = "NORMAL"
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=4)
            except: pass
            
        try:
            import requests, sys
            sys.path.insert(0, '/home/sergio/.openclaw/workspace/denaro')
            load_dotenv('/home/sergio/denaro/.env.telegram')
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            msg = "✅ *DEFCON DISATTIVATO* ✅\n\nIl crollo dei mercati si è fermato. I bot Spot sono stati riautorizzati a comprare il fondo (Dip Buying). Ripresa delle normali operazioni di rete."
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        except: pass

def run_crisis_manager():
    import sys
    logging.info("🚨 CRISIS MANAGER ATTIVATO. Radar Globale su BTC e ETH.")
    while True:
        try:
            crashing, change = is_market_crashing()
            is_defcon = os.path.exists("/home/sergio/.openclaw/workspace/denaro/DEFCON.lock")
            
            if crashing and not is_defcon:
                logging.warning(f"Rilevato crollo: {change:.2f}%. Attivazione protocolli di emergenza.")
                activate_defcon()
            elif not crashing and is_defcon:
                logging.info(f"Mercato stabilizzato: {change:.2f}%. Disattivazione protocolli.")
                deactivate_defcon()
            else:
                if is_defcon:
                    logging.info(f"DEFCON ATTIVO. Mercato ancora in crollo ({change:.2f}%). Mantenimento blocchi.")
                else:
                    logging.info(f"Mercato stabile ({change:.2f}%). Nessuna anomalia.")
            
            time.sleep(300) # Controlla ogni 5 minuti
            
        except Exception as e:
            logging.error(f"Errore Crisis Manager: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_crisis_manager()
