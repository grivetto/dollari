import gc
import os
import time
import pandas as pd
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

# Asset da liquidare a mercato senza condizioni (Reset Capitale)
ASSETS_TO_LIQUIDATE = {
    "AVAX": "AVAXBTC",
    "DOGE": "DOGEBTC",
    "ETH": "ETHBTC",
    "SOL": "SOLBTC"
}

def main():
    print("🧨 PROTOCOLLO 'TABULA RASA' ATTIVATO - LIQUIDAZIONE TOTALE")
    btc_price = float(client.get_symbol_ticker(symbol="BTCEUR")['price'])
    
    for asset, symbol in ASSETS_TO_LIQUIDATE.items():
        try:
            bal = float(client.get_asset_balance(asset=asset)['free'])
            # Filtro per minimi scambiabili su Binance (notional value > 0.0001 BTC)
            ticker = client.get_symbol_ticker(symbol=symbol)
            notional = bal * float(ticker['price'])
            
            if notional > 0.0001:
                print(f"🔄 Liquidazione {asset}: {bal} unità...")
                # Determina precisione per il Lot Size
                info = client.get_symbol_info(symbol)
                step_size = float([f for f in info['filters'] if f['filterType'] == 'LOT_SIZE'][0]['stepSize'])
                precision = 0
                if step_size < 1.0:
                    precision = len(str(step_size).split('.')[-1].rstrip('0'))
                
                qty_str = "{:0.{}f}".format(bal, precision)
                order = client.create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty_str)
                print(f"✅ VENDUTA {asset}. Capitale riportato in BTC.")
                
                # Messaggio su Telegram
                with open('/home/sergio/.openclaw/workspace/denaro/strike_alert.flag', 'w') as f:
                    f.write(f"VENDUTA {asset} (Reset Capitale)")
            else:
                print(f"⏩ {asset} troppo piccola per la vendita ({notional:.6f} BTC)")
        except Exception as e:
            print(f"❌ Errore liquidazione {asset}: {e}")

    print("🏁 RESET COMPLETATO. Il capitale è di nuovo liquido in BTC.")

if __name__ == "__main__":
    main()
