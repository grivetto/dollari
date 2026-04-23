import re

with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

# Update get_dynamic_kb
new_dynamic_kb = """
def get_dynamic_kb():
    try:
        from binance.client import Client
        import os, json
        from dotenv import load_dotenv
        load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
        client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
        balances = client.get_account()['balances']
        assets = {b['asset']: float(b['free']) + float(b['locked']) for b in balances if float(b['free']) > 0 or float(b['locked']) > 0}
        tickers = client.get_all_tickers()
        prices = {t['symbol']: float(t['price']) for t in tickers}
        
        total_eur = assets.get('EUR', 0) + assets.get('USDT', 0)
        for asset, qty in assets.items():
            if asset in ['EUR', 'USDT']: continue
            symbol = f"{asset}EUR"
            if symbol in prices: total_eur += qty * prices[symbol]
            elif f"{asset}BTC" in prices and "BTCEUR" in prices: total_eur += qty * prices[f"{asset}BTC"] * prices["BTCEUR"]
            
        locked = 0.0
        try:
            with open("/home/sergio/.openclaw/workspace/denaro/vault.json", "r") as f:
                data = json.load(f)
                locked = float(data.get("LOCKED_EUR", 0))
        except: pass
        
        profit_today = 0.0
        try:
            with open("/home/sergio/.openclaw/workspace/denaro/daily_mission.json", "r") as f:
                profit_today = float(json.load(f).get("profit_today", 0))
        except: pass
        
        from __main__ import CAPITALE_VERSATO_TOTALE
        profit_total = total_eur - CAPITALE_VERSATO_TOTALE
        
        btn_text = f"Oggi: +{profit_today:.1f}€ | Inv: {CAPITALE_VERSATO_TOTALE:.0f}€ | Ric: +{profit_total:.1f}€"
    except Exception as e:
        btn_text = "Cifra Investita"
        
    return {
        "keyboard": [
            [{"text": btn_text}],
            [{"text": "MEXC Laboratorio"}, {"text": "Stato Squadre"}],
            [{"text": "Andamento Ricavi"}, {"text": "Elemosina Gariban"}],
            [{"text": "Dashboard Web"}]
        ],
        "resize_keyboard": True
    }
"""

# Replace the old get_dynamic_kb function
start_idx = code.find("def get_dynamic_kb():")
end_idx = code.find("def get_mexc_status():")
if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + new_dynamic_kb + "\n" + code[end_idx:]

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)
print("Telegram button patched.")
