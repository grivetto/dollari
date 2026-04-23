import time
import json
import logging
import ccxt
import os
import math
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AI RISK ENGINE 🧠] - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/AI_RISK.log"), logging.StreamHandler()])

load_dotenv('/home/sergio/denaro/.env')
CONFIG_FILE = '/home/sergio/.openclaw/workspace/denaro/trade_config.json'

try:
    binance = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })
except Exception as e:
    logging.error(f"Binance API Error: {e}")
    exit(1)

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1: return 50.0
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def main():
    logging.info("Avvio Motore AI di Allocazione Dinamica del Capitale (Kelly Criterion + RSI).")
    while True:
        try:
            # 1. Fetch market data for BTC
            ohlcv = binance.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=50)
            closes = [x[4] for x in ohlcv]
            
            current_price = closes[-1]
            rsi = calculate_rsi(closes)
            
            # 2. Logic: Buy fear, sell greed
            # Se l'RSI è basso (< 35), il mercato è ipervenduto (paura) -> aumentiamo la size per comprare basso
            # Se l'RSI è alto (> 65), il mercato è ipercomprato (euforia) -> riduciamo la size per limitare l'esposizione
            
            base_size = 15.0
            max_size = 40.0
            min_size = 8.0
            
            # Interpolazione lineare invertita basata sull'RSI
            # RSI 30 -> size = max
            # RSI 70 -> size = min
            
            if rsi <= 30:
                dynamic_size = max_size
                mode = "AGGRESSIVE_DIP_BUYING"
            elif rsi >= 70:
                dynamic_size = min_size
                mode = "DEFENSIVE_TAKE_PROFIT"
            else:
                # Mappa RSI (30-70) a Size (40-8)
                ratio = (rsi - 30) / 40.0 # 0.0 at RSI 30, 1.0 at RSI 70
                dynamic_size = max_size - (ratio * (max_size - min_size))
                mode = "NORMAL_BALANCED"
                
            dynamic_size = round(max(min_size, min(max_size, dynamic_size)), 1)
            
            # Read current config
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                
            old_size = config.get("current_trade_size", 16.0)
            
            # Update only if difference is significant
            if abs(old_size - dynamic_size) > 1.5 or config.get("market_condition") != mode:
                config["current_trade_size"] = dynamic_size
                config["market_condition"] = mode
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=4)
                    
                logging.info(f"RSI BTC/USDT a 15m: {rsi:.2f}. Mercato: {mode}. Nuova Size Globale: {dynamic_size}$ (vecchia: {old_size}$)")
            
        except Exception as e:
            logging.error(f"Errore ciclo AI: {e}")
            
        time.sleep(300) # Controlla ogni 5 minuti

if __name__ == "__main__":
    main()
