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

# Asset da monitorare per chiusura rapida con precisione corretta
ASSETS = {
    "SOL": {"s": "SOLBTC", "p": 3},
    "ETH": {"s": "ETHBTC", "p": 4}, # Corretto a 4 per Filter LOT_SIZE
    "AVAX": {"s": "AVAXBTC", "p": 2},
    "DOGE": {"s": "DOGEBTC", "p": 0}
}

def main():
    print("🚀 PROTOCOLLO CASH-OUT AGGRESSIVO v1.1 (PRECISION FIX)")
    while True:
        try:
            btc_price = float(client.get_symbol_ticker(symbol="BTCEUR")['price'])
            for asset, data in ASSETS.items():
                symbol = data['s']
                precision = data['p']
                
                bal = float(client.get_asset_balance(asset=asset)['free'])
                if bal <= 0.0001: continue
                
                trades = client.get_my_trades(symbol=symbol, limit=1)
                if not trades or not trades[0]['isBuyer']: continue
                entry_price = float(trades[0]['price'])
                
                curr_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
                pnl = (curr_price - entry_price) / entry_price
                
                # VENDITA FORZATA allo 0.18% (Cash out immediato)
                if pnl >= 0.0018:
                    print(f"🎯 TARGET RAGGIUNTO {symbol} (+{pnl:.2%}). Vendo...")
                    try:
                        qty_str = "{:0.{}f}".format(bal, precision)
                        client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty_str)
                        
                        # Calcolo guadagno reale in Euro
                        val_buy = float(trades[0]['quoteQty']) * btc_price
                        profit_eur = val_buy * pnl
                        
                        # CREAZIONE FLAG PER TELEGRAM CON CIFRA REALE
                        with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                            f.write(f"{profit_eur:.2f}")
                            
                        print(f"✅ VENDUTA {asset} | Profitto: €{profit_eur:.2f}")
                    except Exception as e:
                        print(f"❌ Error selling {symbol}: {e}")
            
            gc.collect()
            time.sleep(8)
        except Exception as e:
            print(f"Loop Error: {e}")
            gc.collect()
            time.sleep(20)

if __name__ == "__main__":
    main()
