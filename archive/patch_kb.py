import re

with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

new_kb_logic = """
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
        
        btn_text = f"Cifra: 722€ | Attuale: {total_eur:.0f}€ ({locked:.0f}€)"
    except Exception as e:
        btn_text = "Cifra Investita"
        
    return {
        "keyboard": [
            [{"text": btn_text}, {"text": "Ricavo Giornaliero"}],
            [{"text": "Andamento Ricavi"}, {"text": "Stato Squadre"}],
            [{"text": "Dashboard Web"}, {"text": "Elemosina Gariban"}]
        ],
        "resize_keyboard": True
    }
"""

code = code.replace("def main_loop():", new_kb_logic + "\ndef main_loop():")

# Remove static kb definition
start = code.find("kb = {")
end = code.find("resize_keyboard\": True", start)
if start != -1 and end != -1:
    end = code.find("}", end) + 1
    code = code[:start] + code[end:]

# Inject dynamic kb
target = "if resp_text:\n                            payload = "
code = code.replace(target, "if resp_text:\n                            kb = get_dynamic_kb()\n                            payload = ")

code = code.replace('elif "CIFRA INVESTITA" in text:', 'elif "CIFRA" in text:')

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)
print("Patch applied to telegram_bot_interactive.py")
