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

# Asset che abbiamo già in pancia
ASSETS = {
    "AVAX": "AVAXBTC",
    "DOGE": "DOGEBTC",
    "ETH": "ETHBTC",
    "SOL": "SOLBTC"
}

def main():
    print("🚀 PROTOCOLLO LIQUIDAZIONE IMMEDIATA ATTIVATO")
    while True:
        try:
            for asset, symbol in ASSETS.items():
                # Prendi saldo reale
                bal = float(client.get_asset_balance(asset=asset)['free'])
                if bal <= 0.001: continue # Saldo nullo o trascurabile
                
                # Prendi ultimo prezzo di acquisto reale
                trades = client.get_my_trades(symbol=symbol, limit=1)
                if not trades: continue
                entry_price = float(trades[0]['price'])
                
                # Prezzo attuale
                curr_ticker = client.get_symbol_ticker(symbol=symbol)
                curr_price = float(curr_ticker['price'])
                
                pnl = (curr_price - entry_price) / entry_price
                print(f"Checking {symbol}: PnL {pnl:+.4f}")

                # VENDITA FORZATA: Appena siamo in attivo anche solo dello 0.1% (per coprire commissioni e uscire)
                if pnl >= 0.0015: 
                    print(f"🎯 TARGET RAGGIUNTO per {symbol}. Eseguo SELL...")
                    try:
                        client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=bal)
                        print(f"✅ VENDITA ESEGUITA: {symbol}")
                        with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                            f.write(f"VENDITA {asset} OK")
                    except Exception as e:
                        print(f"❌ ERRORE SELL {symbol}: {e}")
            
            gc.collect()
            time.sleep(5) # Ciclo velocissimo
        except Exception as e:
            print(f"Loop Error: {e}")
            gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
