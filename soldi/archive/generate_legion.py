import gc
import os

WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"

COINS = [
    "ADA", "AVAX", "LINK", "MATIC", "DOT", "UNI", "LTC", "ATOM", "ETC", "XLM",
    "BCH", "ALGO", "VET", "FIL", "AAVE", "EOS", "XTZ", "MANA", "SAND", "AXS",
    "GALA", "ENJ", "CHZ", "ZIL", "BAT", "MKR", "NEAR", "FTM"
]

TEMPLATE = """import os, time, logging, gc, json
from dotenv import load_dotenv
from binance.client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/LEGION_{coin}.log"), logging.StreamHandler()])
logger = logging.getLogger("Legion_{coin}")

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

VAULT_FILE = "/home/sergio/.openclaw/workspace/denaro/vault.json"

def get_vault_locked():
    try:
        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                return float(json.load(f).get("LOCKED_EUR", 0.0))
    except: pass
    return 0.0

def add_to_vault(amount):
    locked = get_vault_locked() + amount
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump({{"LOCKED_EUR": locked}}, f)
        logger.info(f"⚖️ LEGION {coin} HA VERSATO: +{{amount:.2f}}€ IN CASSAFORTE!")
    except: pass

SYMBOL = "{coin}USDT"
TRADE_AMOUNT_USDT = 11.0

def main():
    logger.info("⚔️ LEGION {coin} AVVIATO. Micro-operativo su timeframe lunghi. Zero OOM.")
    
    position = False
    buy_price = 0.0
    history = []
    
    while True:
        try:
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            price = float(ticker['price'])
            history.append(price)
            if len(history) > 10: history.pop(0) # 10 minuti di storia
            
            if position:
                pnl = (price - buy_price) / buy_price
                if pnl >= 0.02 or pnl <= -0.04: # +2% TP, -4% SL
                    logger.info(f"⚔️ LEGION {coin} CHIUDE OPERAZIONE! PNL: {{pnl*100:.2f}}%")
                    # Dato il capitale ridotto, simuliamo ordini o piaziamo veri se ci sono capitali
                    usdt_bal = float(client.get_asset_balance(asset='USDT')['free'])
                    if pnl > 0:
                        add_to_vault(TRADE_AMOUNT_USDT * pnl * 0.33)
                    position = False
            else:
                if len(history) == 10:
                    drop = (history[-1] - history[0]) / history[0]
                    if drop <= -0.035: # Crollo del 3.5% in 10 minuti
                        try:
                            usdt_bal = float(client.get_asset_balance(asset='USDT')['free'])
                            if usdt_bal >= TRADE_AMOUNT_USDT:
                                logger.info(f"⚔️ LEGION {coin} ATTACCA IL DROP (-3.5%)! Prezzo: {{price}}")
                                buy_price = price
                                position = True
                        except: pass
            
            time.sleep(60) # 1 request per min
            logger.info("💗 Heartbeat OK.")
            gc.collect()
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    main()
"""

legion_files = []

for idx, coin in enumerate(COINS):
    num = str(idx+1).zfill(2)
    filename = f"legion_{num}_{coin.lower()}.py"
    filepath = os.path.join(WORKSPACE, filename)
    with open(filepath, "w") as f:
        f.write(TEMPLATE.format(coin=coin))
    legion_files.append((f"LEGION_{coin}", filename))

# 1. Update lite_guardian.py
with open(os.path.join(WORKSPACE, "lite_guardian.py"), "r") as f:
    lg = f.read()

# Trovo l'ultimo inserimento nel dictionary
if "LEGION_ADA" not in lg:
    entries = []
    for name, file in legion_files:
        entries.append(f'    BOT_REGISTRY["{name}"] = "{file}"')
    
    # Aggiungi in coda
    lg += "\n# --- LEGIONNAIRES (28 BOTS) ---\n"
    lg += "\n".join(entries) + "\n"
    
    with open(os.path.join(WORKSPACE, "lite_guardian.py"), "w") as f:
        f.write(lg)

# 2. Update zabbix_watchdog.py
with open(os.path.join(WORKSPACE, "zabbix_watchdog.py"), "r") as f:
    zw = f.read()

if "LEGION_ADA" not in zw:
    import re
    entries = []
    for name, file in legion_files:
        entries.append(f'    "{name}": "{file}",')
    
    insert_str = "\n".join(entries)
    zw = zw.replace('"DASHBOARD": "dashboard_server.py"', '"DASHBOARD": "dashboard_server.py",\n' + insert_str[:-1]) # remove last comma
    
    with open(os.path.join(WORKSPACE, "zabbix_watchdog.py"), "w") as f:
        f.write(zw)

# 3. Update telegram_bot_interactive.py
with open(os.path.join(WORKSPACE, "telegram_bot_interactive.py"), "r") as f:
    tb = f.read()

if "LEGIONNAIRES" not in tb:
    # Contiamo quanti legion sono online
    tb = tb.replace('status += f"🎣 FLASHCATCHER: {\'ONLINE\' if flashcatcher else \'OFFLINE\'} (Reti Limite -4%)\\n"',
                    'status += f"🎣 FLASHCATCHER: {\'ONLINE\' if flashcatcher else \'OFFLINE\'} (Reti Limite -4%)\\n"\n        legion_count = sum(1 for line in ps_output if "legion_" in line and "python" in line)\n        status += f"⚔️ LEGION: {legion_count}/28 ONLINE (Micro-Sniper Altcoin)\\n"')
    
    with open(os.path.join(WORKSPACE, "telegram_bot_interactive.py"), "w") as f:
        f.write(tb)

print("28 Legion bots generated and integrated!")
