import gc
import gc
import gc
import ccxt
import os
import time
import logging
import json
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [IL GENERALE 🎖️] - %(message)s',
                    handlers=[logging.FileHandler("IL_GENERALE.log"), logging.StreamHandler()])
logger = logging.getLogger("IlGenerale")

load_dotenv('/home/sergio/denaro/.env')

binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'adjustForTimeDifference': True}
})

VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

def get_vault_locked():
    try:
        with open(VAULT_FILE, 'r') as f:
            return float(json.load(f).get("LOCKED_EUR", 0.0))
    except: return 0.0

def get_market_trend(symbol):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, '1h', limit=24)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        trend_24h = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
        return trend_24h
    except: return 0.0

def run_generale():
    logger.info("🎖️ IL GENERALE È SUL CAMPO. Avvio riallocazione dinamica del capitale.")
    
    import gc
while True:
        gc.collect()
        try:
            bal = binance.fetch_balance()
            total_eur = bal.get('EUR', {}).get('total', 0.0)
            free_eur = bal.get('EUR', {}).get('free', 0.0)
            locked_vault = get_vault_locked()
            usable_eur = free_eur - 5.0
            
            logger.info(f"📊 Rapporto Capitale: Disponibile {usable_eur:.2f}€ (su {total_eur:.2f}€ totali). Vault protetto: {locked_vault:.2f}€")
            
            # 1. Ispezione Truppe (Posizioni aperte su Altcoin)
            for asset, asset_data in bal['free'].items():
                if asset in ['EUR', 'USDT', 'USDC'] or asset_data <= 0: continue
                symbol = f"{asset}/EUR"
                
                try:
                    ticker = binance.fetch_ticker(symbol)
                    value_eur = asset_data * ticker['last']
                    
                    if value_eur < 10.0: continue # Ignoriamo la polvere
                    
                    trend = get_market_trend(symbol)
                    
                    # 2. Taglio Ramo Secco (Se perde da 24h e trend è < -5%)
                    if trend < -5.0:
                        logger.warning(f"✂️ TAGLIO TATTICO: {symbol} in caduta libera ({trend:+.2f}%). Il Generale liquida la posizione per salvare il capitale.")
                        try:
                            # Vendiamo per recuperare EUR
                            free_asset = float(bal['free'].get(asset, 0.0))
                            qty = float(binance.amount_to_precision(symbol, free_asset * 0.99))
                            binance.create_market_sell_order(symbol, qty)
                            logger.info(f"✅ Recuperati ~{value_eur:.2f}€ da {asset}")
                        except Exception as e:
                            logger.error(f"Errore vendita {asset}: {e}")
                            
                    # 3. Potenziamento Cavallo Vincente
                    elif trend > 5.0 and usable_eur > 15.0:
                        logger.info(f"🔥 CAVALLO VINCENTE: {symbol} sta volando ({trend:+.2f}%). Il Generale stanzia rinforzi immediati!")
                        try:
                            # Compriamo 30 EUR extra su questo asset
                            qty = binance.amount_to_precision(symbol, 15.0 / ticker['last'])
                            binance.create_market_buy_order(symbol, float(qty))
                            usable_eur -= 15.0
                            logger.info(f"🚀 Iniettati 30€ su {symbol}")
                        except Exception as e:
                            logger.error(f"Errore rinforzo {asset}: {e}")
                except: pass

            logger.info("⛺ Il Generale torna in tenda per pianificare la prossima mossa (Pausa 1 ora).")
            time.sleep(3600)

        except Exception as e:
            logger.error(f"Errore critico del Generale: {e}")
            time.sleep(60)

if __name__ == '__main__':
    run_generale()
