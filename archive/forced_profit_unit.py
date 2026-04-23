import gc
import gc
import gc
import gc
import os
import time
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

# Protocollo "ESTRAZIONE FORZATA" - Solo le top monete più liquide
SYMBOLS = ["SOLBTC", "AVAXBTC", "ETHBTC"]
RISK_BTC = 0.003 # ~180€ per colpo (MASSIMA POTENZA)

def main():
    print("🚀 PROTOCOLLO CASH-OUT ATTIVATO")
    while True:
        try:
            for s in SYMBOLS:
                # Analisi ultra-veloce RSI 2 periodi (iper-aggressivo)
                klines = client.get_klines(symbol=s, interval='1m', limit=10)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                price = float(df['c'].iloc[-1])
                
                # Entra se il prezzo scende minimamente (Buy the micro-dip)
                if float(df['c'].iloc[-1]) < float(df['c'].iloc[-2]):
                    print(f"🎯 ATTACCO FLASH: {s}")
                    try:
                        order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                        qty = float(order['executedQty'])
                        
                        # VENDITA FORZATA allo 0.3% (Guadagno immediato, pochi secondi)
                        target = price * 1.003
                        print(f"🛒 In attesa target €{target}...")
                        
                        while True:
                            now = float(client.get_symbol_ticker(symbol=s)['price'])
                            if now >= target:
                                client.create_order(symbol=s, side='SELL', type='MARKET', quantity=qty)
                                print(f"✅ INCASSATO: {s}")
                                with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f: f.write("PROFITTO REALE")
                                break
                            gc.collect()
            time.sleep(2)
                    except: pass
            gc.collect()
            time.sleep(5)
        except: gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
