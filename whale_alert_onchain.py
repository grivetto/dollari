import requests
import json
import logging
import time
import os
from dotenv import load_dotenv
import telegram_bot_interactive as tbi

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [WHALE 🐋] - %(message)s',
                    handlers=[logging.FileHandler("WHALE_ONCHAIN.log"), logging.StreamHandler()])

load_dotenv('/home/sergio/denaro/.env')
load_dotenv('/home/sergio/denaro/.env.telegram')

# Whale Alert API gratuita o scraping
# Poiché l'API Whale Alert richiede una chiave a pagamento, simuliamo un radar su una fonte open (es. Coinglass o scraping Twitter RSS/Telegram public channels)
# Per il MVP (Minimum Viable Product), useremo l'Open Interest e i Volumi anormali di Binance Futures come proxy "On-Chain" gratuito.

def check_anomalous_volume():
    try:
        import ccxt
        binance_f = ccxt.binance({'options': {'defaultType': 'future'}})
        
        # Guardiamo BTC e SOL
        btc = binance_f.fetch_ticker('BTC/USDT')
        sol = binance_f.fetch_ticker('SOL/USDT')
        
        # Se i volumi 24h salgono in maniera anomala o c'è uno spread assurdo, allerta balena
        if btc['quoteVolume'] > 50000000000: # 50 Miliardi
            return True, "BTC", "MASSIVE VOLUME DETECTED (>50B)"
            
        return False, "", ""
    except Exception as e:
        return False, "", ""

def run_whale_tracker():
    logging.info("🐋 ON-CHAIN WHALE TRACKER INIZIALIZZATO. (Proxy Mode su Open Interest e Volume).")
    while True:
        try:
            detected, coin, reason = check_anomalous_volume()
            if detected:
                logging.warning(f"🚨 BALENA RILEVATA SU {coin}: {reason}")
                
                # Se troviamo una balena in vendita, diciamo ai bot di prepararsi allo SHORT
                config_path = "/home/sergio/.openclaw/workspace/denaro/trade_config.json"
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r") as f:
                            config = json.load(f)
                        config["whale_alert"] = coin
                        with open(config_path, "w") as f:
                            json.dump(config, f, indent=4)
                    except: pass
                    
            time.sleep(300) # 5 min
        except Exception as e:
            logging.error(f"Errore Whale: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_whale_tracker()
