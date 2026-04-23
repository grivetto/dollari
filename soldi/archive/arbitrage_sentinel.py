import gc
import gc
import gc
import os
import time
import requests
import logging
import json
from binance.client import Client
from dotenv import load_dotenv

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('arbitrage_sentinel.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_binance_price(symbol):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
        return float(r.json()['price'])
    except: return None

def get_cryptocom_price(instrument):
    try:
        r = requests.get(f"https://api.crypto.com/v2/public/get-ticker?instrument_name={instrument}")
        return float(r.json()['result']['data'][0]['a'])
    except: return None

def main():
    load_dotenv()
    logger.info("🚀 Arbitrage Sentinel v1.0 - Monitoraggio spread iniziato")
    
    # Coppie da monitorare (Normalizzate su USD/USDT per confronto)
    # Esempio: SOL/EUR su Binance vs SOL/USDT su Crypto.com (convertito)
    
    while True:
        try:
            # 1. Recupera prezzi SOL
            binance_sol_eur = get_binance_price("SOLEUR")
            # Approssimiamo EUR/USD a 1.08
            binance_sol_usd = binance_sol_eur * 1.08 if binance_sol_eur else None
            
            crypto_sol_usdt = get_cryptocom_price("SOL_USDT")
            
            if binance_sol_usd and crypto_sol_usdt:
                spread = abs(binance_sol_usd - crypto_sol_usdt)
                spread_pct = (spread / binance_sol_usd) * 100
                
                if spread_pct > 1.2: # Soglia opportunità (oltre commissioni)
                    logger.info(f"💎 OPPORTUNITÀ ARBITRAGGIO: Spread {spread_pct:.2f}% | B: ${binance_sol_usd:.2f} vs C: ${crypto_sol_usdt:.2f}")
                
                # Salva sempre per la dashboard
                with open('/home/sergio/.openclaw/workspace/denaro/dashboard/arbitrage_data.json', 'w') as f:
                    json.dump({"time": time.strftime('%H:%M:%S'), "spread": f"{spread_pct:.2f}%", "b_price": f"${binance_sol_usd:.2f}", "c_price": f"${crypto_sol_usdt:.2f}"}, f)
            
            gc.collect()
            time.sleep(60)
        except Exception as e:
            logger.error(f"Errore Monitor: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
