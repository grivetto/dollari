import ccxt
import os
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.bitget')

try:
    bitget = ccxt.bitget({
        'apiKey': os.getenv('BITGET_API_KEY'),
        'secret': os.getenv('BITGET_API_SECRET'),
        'password': os.getenv('BITGET_PASSWORD'),
        'enableRateLimit': True,
    })
    positions = bitget.fetch_positions()
    active_positions = [p for p in positions if float(p.get('contracts', 0) or 0) > 0]
    if not active_positions:
        print("Nessuna posizione aperta su Bitget.")
    else:
        for p in active_positions:
            symbol = p['symbol']
            side = p['side']
            unrealizedPnl = float(p.get('unrealizedPnl', 0) or 0)
            contracts = p.get('contracts')
            print(f"[{symbol} {side}] Contratti: {contracts} | PnL Latente: {unrealizedPnl:.4f}$")
except Exception as e:
    print(f"Errore: {e}")
