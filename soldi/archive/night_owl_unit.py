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

# SQUADRA NOTTURNA: NIGHT OWL UNIT
# Obiettivo: Sfruttare la volatilità asiatica e i volumi notturni
SYMBOLS = ["SOLBTC", "AVAXBTC", "ETHBTC", "LINKBTC", "ADABTC", "DOGEBTC", "PEPEBTC", "FETBTC"]
RISK_BTC = 0.0035 # Forza d'urto aumentata per la notte (~200€)

def main():
    print("🌙 NIGHT OWL UNIT ACTIVATED - OVERNIGHT STRIKE MODE")
    active_hunts = {}

    while True:
        try:
            btc_bal = float(client.get_asset_balance(asset='BTC')['free'])
            
            for s in SYMBOLS:
                # 1. Scansione volatilità 1 minuto (Caccia allo Spike)
                klines = client.get_klines(symbol=s, interval='1m', limit=3)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                df['c'] = pd.to_numeric(df['c'])
                
                price = df['c'].iloc[-1]
                
                # Segnale NOTTURNO: Salita improvvisa dello 0.2% in 60 secondi
                if price > df['c'].iloc[-2] * 1.002 and s not in active_hunts:
                    if btc_bal >= RISK_BTC:
                        print(f"🔥 SPIKE NOTTURNO RILEVATO su {s}! Inseguimento attivo.")
                        try:
                            order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                            qty = float(order['executedQty'])
                            active_hunts[s] = {'entry': price, 'qty': qty, 'max': price}
                        except: pass

                # 2. Gestione Uscita (Target Rapido 0.35% o Drop 0.15%)
                if s in active_hunts:
                    if price > active_hunts[s]['max']: active_hunts[s]['max'] = price
                    
                    entry = active_hunts[s]['entry']
                    max_p = active_hunts[s]['max']
                    pnl = (price - entry) / entry
                    drop = (max_p - price) / max_p
                    
                    # Vendita rapida per sbloccare euro
                    if pnl >= 0.0035 or drop >= 0.0015:
                        print(f"💰 INCASSO NOTTURNO su {s} (+{pnl:.2%})")
                        try:
                            client.create_order(symbol=s, side='SELL', type='MARKET', quantity=active_hunts[s]['qty'])
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"NOTTE {s.replace('BTC','')}: +{pnl:.2%}")
                            del active_hunts[s]
                        except: pass
            
            gc.collect()
            time.sleep(5)
        except: gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
