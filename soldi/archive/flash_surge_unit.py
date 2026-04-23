import gc
import gc
import os
import time
import json
import logging
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

# CONFIGURAZIONE FLASH (ULTRA-AGGRESSIVA)
SYMBOLS = ["AVAXEUR", "DOGEEUR", "SOLEUR", "ETHEUR", "BNBEUR", "LINKEUR", "PEPEEUR", "SHIBEUR"]
RISK_BTC = 30.0 # 30 EUR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("FLASH")

def main():
    logger.info("⚡ FLASH SURGE UNIT - SCALPING FORZATO ATTIVO")
    positions = {}
    
    while True:
        try:
            for s in SYMBOLS:
                try:
                    klines = client.get_klines(symbol=s, interval='1m', limit=20)
                    df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                    df['c'] = pd.to_numeric(df['c'])
                    
                    ema = ta.ema(df['c'], length=9).iloc[-1]
                    rsi = ta.rsi(df['c'], length=7).iloc[-1]
                    price = df['c'].iloc[-1]
                    
                    # Ingressi ancora più facili
                    if rsi > 45 and price > ema and s not in positions:
                        logger.info(f"🚀 FLASH ENTRY: {s}")
                        try:
                            order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                            positions[s] = {'entry': float(order['fills'][0]['price']), 'time': time.time(), 'qty': float(order['executedQty'])}
                        except Exception as e:
                            logger.error(f"❌ FLASH ENTRY FAILED {s}: {e}")
                except Exception as e:
                    logger.debug(f"Error processing {s}: {e}")
                
                gc.collect()
                
                # Gestione uscite
                if s in positions:
                    try:
                        entry_price = positions[s]['entry']
                        qty = positions[s]['qty']
                        ticker = client.get_symbol_ticker(symbol=s)
                        current_price = float(ticker['price'])
                        pnl = (current_price - entry_price) / entry_price
                        
                        # Uscita a 0.4% profitto o -1% stop loss o timeout 3 minuti
                        if pnl >= 0.004 or pnl <= -0.01 or (time.time() - positions[s]['time'] > 180):
                            try:
                                order = client.create_order(symbol=s, side='SELL', type='MARKET', quantity=qty)
                                exit_price = float(order['fills'][0]['price'])
                                actual_pnl = (exit_price - entry_price) / entry_price
                                logger.info(f"✅ FLASH SELL: {s} PnL: {actual_pnl:+.2%}")
                                
                                # Registra lo strike per la dashboard
                                try:
                                    with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                        f.write(f"{s}:{actual_pnl:+.2%}")
                                except:
                                    pass
                                
                                del positions[s]
                            except Exception as e:
                                logger.error(f"❌ FLASH SELL FAILED {s}: {e}")
                    except Exception as e:
                        logger.debug(f"Error checking exit for {s}: {e}")
                
                time.sleep(2)  # Pausa tra simboli
            
            time.sleep(10)  # Ciclo principale
            
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
