import gc
import gc
import gc
import os
import time
import requests
import json
import logging
from binance.client import Client
from dotenv import load_dotenv

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler('sentinel_trend.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
    
    # Coppie da monitorare per opportunità improvvise
    WATCHLIST = ["BTCEUR", "ETHEUR", "SOLEUR", "BNBEUR", "ADAEUR"]
    
    logger.info(f"🚀 Sentinel Trend Bot Attivo su {len(WATCHLIST)} coppie")

    while True:
        try:
            signals = []
            for symbol in WATCHLIST:
                # Recupera klines a 1m per rilevare spike di volume/prezzo
                klines = client.get_klines(symbol=symbol, interval='1m', limit=5)
                # Calcola variazione percentuale ultimo minuto
                start_price = float(klines[0][4])
                end_price = float(klines[-1][4])
                change = (end_price - start_price) / start_price
                
                if abs(change) >= 0.001: # Soglia ridotta per test (0.1%)
                    direction = "🚀 UP" if change > 0 else "🔻 DOWN"
                    logger.info(f"⚠️ OPPORTUNITÀ RILEVATA: {symbol} {direction} ({change:.2%})")
                    signals.append({
                        "time": time.strftime('%H:%M:%S'),
                        "symbol": symbol,
                        "change": f"{change:.2%}",
                        "direction": direction
                    })
            
            # Scrivi sempre il file (anche se vuoto) per evitare 404 sulla dashboard
            with open('/home/sergio/.openclaw/workspace/denaro/dashboard/sentinel_data.json', 'w') as f:
                json.dump(signals, f)
            
            gc.collect()
            time.sleep(30)
        except Exception as e:
            logger.error(f"Errore Sentinel: {e}")
            gc.collect()
            time.sleep(60)

if __name__ == "__main__":
    main()
