#!/usr/bin/env python3
"""Acquisto €30 di BTC per testare il sistema e iniziare l'accumulo."""
import ccxt
from dotenv import load_dotenv
import os

# Carica chiavi dalla configurazione Nuvola (che sappiamo funzionare)
load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

print(f"Chiave attiva: {api_key[:10]}...")

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

try:
    # Prezzi attuali
    ticker = exchange.fetch_ticker('BTC/EUR')
    price = ticker['last']
    print(f"Prezzo attuale BTC: €{price:.2f}")

    # Calcolo importo
    amount_eur = 30.0
    btc_amount = (amount_eur / price) * 0.998  # meno fee
    print(f"Acquisto di {btc_amount:.6f} BTC (~€{amount_eur})")

    # Esegui ordine
    order = exchange.create_market_buy_order('BTC/EUR', btc_amount)
    
    print(f"\n✅ ORDINE ESEGUITO!")
    print(f"ID: {order['id']}")
    print(f"Stato: {order['status']}")
    print(f"Prezzo medio: {order.get('average', price):.2f}")

except Exception as e:
    print(f"❌ Errore acquisto: {e}")
