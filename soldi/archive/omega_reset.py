import gc
import os
import time
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

# Protocollo OMEGA LIQUIDATION
# Vende tutto ciò che è in pancia per resettare il capitale e permettere alla Triade di ripartire
ASSETS = {
    "ETH": {"s": "ETHBTC", "p": 4},
    "SOL": {"s": "SOLBTC", "p": 3},
    "AVAX": {"s": "AVAXBTC", "p": 2},
    "ADA": {"s": "ADABTC", "p": 0}
}

def main():
    print("🧨 OMEGA LIQUIDATION SEQUENCE INITIATED")
    for asset, data in ASSETS.items():
        try:
            bal = float(client.get_asset_balance(asset=asset)['free'])
            if bal > 0.0001:
                print(f"🔄 Liquidazione {asset}...")
                qty_str = "{:0.{}f}".format(bal, data['p'])
                client.create_order(symbol=data['s'], side='SELL', type='MARKET', quantity=qty_str)
                print(f"✅ {asset} convertito in BTC.")
        except Exception as e:
            print(f"❌ Errore {asset}: {e}")
    print("🏁 RESET OMEGA COMPLETATO.")

if __name__ == "__main__":
    main()
