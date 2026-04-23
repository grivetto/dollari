#!/usr/bin/env python3
"""
STRATEGIA: Vendita asset morti -> Comprare ETH -> Sbloccare Grid Bot
"""
import ccxt
import os
import time
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

def run():
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })

    print("=== FASE 1: VENDITA ASSET MORTI ===")
    
    assets_to_sell = [
        {'symbol': 'SOL/EUR', 'check': 'SOL'},
        {'symbol': 'AVAX/EUR', 'check': 'AVAX'},
        {'symbol': 'BNB/EUR', 'check': 'BNB'}
    ]

    total_sold = 0

    for asset in assets_to_sell:
        balance = exchange.fetch_balance()
        free = balance.get(asset['check'], {}).get('free', 0)
        
        if free > 0:
            try:
                print(f"Vendo {free} {asset['check']}...")
                order = exchange.create_market_sell_order(asset['symbol'], free)
                print(f"✅ Ordine eseguito. ID: {order['id']}")
                total_sold += 1
            except Exception as e:
                print(f"❌ Errore vendita {asset['check']}: {e}")
        else:
            print(f"- {asset['check']} vuoto o già venduto.")
        
        time.sleep(1) # Rate limit

    print(f"\nAttesa consolidamento fondi (5s)...")
    time.sleep(5)

    print("=== FASE 2: COMPRA ETH PER GRID BOT ===")
    
    # Check Balance
    balance = exchange.fetch_balance()
    eur = balance.get('EUR', {}).get('free', 0)
    print(f"Euro liberi: €{eur:.2f}")

    # Calcoliamo ETH necessaria. Attualmente ne abbiamo poca (0.04).
    # Per fare 4 sell orders da €35, serviamo circa 0.076 ETH.
    # Ne compriamo per circa €60-70 EUR.
    buy_amount_eur = 60 
    
    eth_balance = balance.get('ETH', {}).get('free', 0)
    price = exchange.fetch_ticker('ETH/EUR')['last']
    print(f"Prezzo ETH: €{price}")
    print(f"ETH attuale: {eth_balance}")
    
    if eur > buy_amount_eur:
        amount_eth = (buy_amount_eur / price) * 0.995
        print(f"Compro {amount_eth:.4f} ETH (~€{buy_amount_eur})...")
        try:
            order = exchange.create_market_buy_order('ETH/EUR', amount_eth)
            print(f"✅ Acquisto ETH effettuato.")
        except Exception as e:
            print(f"❌ Errore acquisto ETH: {e}")
    else:
        print(f"⚠️ Euro insufficienti per comprare ETH.")

    # Final Balance
    print("\n=== BILANCIO FINALE ===")
    final_bal = exchange.fetch_balance()
    eur_f = final_bal.get('EUR', {}).get('free', 0)
    eth_f = final_bal.get('ETH', {}).get('free', 0)
    print(f"Euro: €{eur_f:.2f}")
    print(f"ETH: {eth_f:.4f}")
    print(f"Totale stimato (ETH+EUR): €{eur_f + (eth_f * price):.2f}")

if __name__ == "__main__":
    run()