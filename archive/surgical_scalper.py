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

# CONFIGURAZIONE SURGICAL SCALPER v1.1 - ULTRA AGGRESSIVE
SYMBOLS = ["SOLBTC", "ETHBTC", "AVAXBTC", "LINKBTC", "ADABTC", "DOGEBTC"]
RISK_BTC = 0.003 # ~180€ per operazione per sentire il profitto

def main():
    print("🚀 SURGICAL SCALPER v1.1 - ULTRA-FAST ACTIVATED")
    while True:
        try:
            btc_bal = float(client.get_asset_balance(asset='BTC')['free'])
            for s in SYMBOLS:
                if btc_bal < RISK_BTC: break # Liquido finito
                
                # Prendi dati 1 minuto
                klines = client.get_klines(symbol=s, interval='1m', limit=3)
                if len(klines) < 3: continue
                
                c2 = float(klines[-1][4]) # Chiusura attuale
                c1 = float(klines[-2][4]) # Chiusura precedente
                
                # SEGNALE FLASH: Appena la candela da 1m è verde, entra.
                if c2 > c1:
                    print(f"🎯 ATTACCO FLASH su {s}")
                    try:
                        order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                        qty = float(order['executedQty'])
                        entry = float(order['fills'][0]['price']) if order['fills'] else c2
                        
                        # TARGET DI USCITA RIDICOLO: 0.15% (Vogliamo lo strike veloce!)
                        target = entry * 1.0015
                        print(f"🛒 In attesa target {target:.8f}...")
                        
                        start_wait = time.time()
                        while time.time() - start_wait < 120: # Timeout 2 minuti per non restare incastrati
                            now = float(client.get_symbol_ticker(symbol=s)['price'])
                            if now >= target:
                                client.create_order(symbol=s, side='SELL', type='MARKET', quantity=qty)
                                profit_eur = (RISK_BTC * 0.0015 * 59000)
                                print(f"✅ INCASSATO {s} (+0.15%) -> €{profit_eur:.2f}")
                                with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                    f.write(f"{profit_eur:.2f}")
                                break
                            gc.collect()
            time.sleep(1)
                        
                        # Se dopo 2 minuti non ha venduto, esci comunque in pari o leggero loss per riprovare
                        if s in client.get_asset_balance(asset=s.replace('BTC',''))['free']:
                            # Controllo se ho ancora la posizione
                            bal_now = float(client.get_asset_balance(asset=s.replace('BTC',''))['free'])
                            if bal_now >= qty:
                                client.create_order(symbol=s, side='SELL', type='MARKET', quantity=qty)
                                print(f"⏱️ TIMEOUT {s} - Posizione chiusa forzatamente.")
                    except Exception as e:
                        print(f"❌ Error in trade {s}: {e}")
            
            gc.collect()
            time.sleep(5)
        except Exception as e:
            print(f"Main Loop Error: {e}")
            gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
