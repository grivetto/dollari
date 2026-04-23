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

# Strategia "Sergio Wave Rider"
# 1. Scansiona chi sale ed entra.
# 2. Vende al PRIMO accenno di discesa.
SYMBOLS = ["SOLBTC", "AVAXBTC", "ETHBTC", "ADABTC", "LINKBTC", "DOGEBTC"]
RISK_BTC = 0.003 # ~180€

def main():
    print("🌊 PROTOCOLLO SERGIO WAVE RIDER ONLINE")
    active_waves = {}

    while True:
        try:
            # Check bilancio per nuovi ingressi
            btc_bal = float(client.get_asset_balance(asset='BTC')['free'])
            
            for s in SYMBOLS:
                # 1. RILEVAMENTO SALITA (1 min)
                klines = client.get_klines(symbol=s, interval='1m', limit=5)
                df = pd.DataFrame(klines, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tq', 'i'])
                current = float(df['c'].iloc[-1])
                
                # Se la candela attuale è più alta della precedente e di quella ancora prima
                is_rising = current > float(df['c'].iloc[-2]) > float(df['c'].iloc[-3])
                
                if is_rising and s not in active_waves and btc_bal >= RISK_BTC:
                    print(f"🏄 SALITA RILEVATA su {s}. Entro in corsa!")
                    try:
                        order = client.create_order(symbol=s, side='BUY', type='MARKET', quoteOrderQty=round(RISK_BTC, 6))
                        active_waves[s] = {'entry': current, 'qty': float(order['executedQty']), 'highest': current}
                    except: pass

                # 2. RILEVAMENTO DISCESA (Sergio Rule)
                if s in active_waves:
                    if current > active_waves[s]['highest']:
                        active_waves[s]['highest'] = current
                    
                    # Se il prezzo scende anche solo di un soffio dal massimo (-0.15%) -> VENDI SUBITO
                    if current < active_waves[s]['highest'] * 0.9985:
                        print(f"📉 {s} ha iniziato a scendere. Esco subito come ordinato.")
                        try:
                            client.create_order(symbol=s, side='SELL', type='MARKET', quantity=active_waves[s]['qty'])
                            pnl = (current - active_waves[s]['entry']) / active_waves[s]['entry']
                            with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                                f.write(f"SERGIO WAVE {s.replace('BTC','')}: {pnl:+.2%}")
                            del active_waves[s]
                        except: pass
            
            # Gestione extra: se abbiamo monete "orfane", Wave Rider le adotta e le vende se scendono
            for a in ["ETH", "SOL", "AVAX", "ADA"]:
                bal = float(client.get_asset_balance(asset=a)['free'])
                if bal > 0.01 and f"{a}BTC" not in active_waves:
                    # Ticker attuale
                    price = float(client.get_symbol_ticker(symbol=f"{a}BTC")['price'])
                    active_waves[f"{a}BTC"] = {'entry': price, 'qty': bal, 'highest': price}

            gc.collect()
            time.sleep(5)
        except: gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
