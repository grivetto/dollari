import gc
import gc
import gc
import os
import json
import time
import logging
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv

# --- CONFIGURAZIONE MONITOR ---
load_dotenv()
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# Mappa delle squadre e dei bot
TRIAD_MAP = {
    "ALPHA": {
        "CORE": "binance_bot_multi.py",
        "WAVE_RIDER": "sergio_wave_rider.py",
        "SURGE": "flash_surge_unit.py",
        "QUANT": "advanced_quant_bot.py"
    },
    "OMEGA": {
        "CORE": "omega_war_machine.py",
        "SHIELD": "centurion_reversion_squad.py",
        "FEEDER": "omega_bottom_feeder.py",
        "REVERSE": "contrarian_omega_squad.py"
    },
    "SYSTEM": {
        "ARCHITECT": "architect_ai.py",
        "EVOLUTION": "evolution_engine.py",
        "MONITOR": "triad_sentinel_automa.py"
    }
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AUTOMA] - %(message)s')
logger = logging.getLogger("Automa")

def get_process_status():
    ps_output = os.popen("ps aux").read()
    status = {}
    for squad, bots in TRIAD_MAP.items():
        status[squad] = {}
        for bot_name, script in bots.items():
            status[squad][bot_name] = "ONLINE" if script in ps_output else "OFFLINE"
    return status

def get_market_vitals():
    try:
        client = Client(API_KEY, API_SECRET)
        btc_price = float(client.get_symbol_ticker(symbol="BTCEUR")['price'])
        # Portfolio real-time sync
        balances = client.get_account()['balances']
        total_eur = 0.0
        active_assets = []
        
        # Filtriamo asset significativi
        for b in balances:
            free = float(b['free'])
            locked = float(b['locked'])
            qty = free + locked
            if qty > 0:
                asset = b['asset']
                if asset == 'EUR': total_eur += qty
                elif asset == 'USDT': total_eur += qty # 1:1
                else:
                    try:
                        price = float(client.get_symbol_ticker(symbol=f"{asset}BTC")['price']) * btc_price if asset != 'BTC' else btc_price
                        val = qty * price
                        if val > 0.5:
                            total_eur += val
                            active_assets.append({"asset": asset, "val": round(val, 2)})
                    except: pass
        
        return {
            "btc_price": btc_price,
            "total_val": round(total_eur, 2),
            "profit": round(total_eur - 722.00, 2),
            "assets": active_assets
        }
    except: return None

def main():
    logger.info("🤖 TRIAD SENTINEL AUTOMA STARTING...")
    while True:
        try:
            vitals = get_market_vitals()
            squad_status = get_process_status()
            
            payload = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vitals": vitals,
                "squads": squad_status,
                "dna_gen": 15 # Placeholder per Evolution Engine integration
            }
            
            with open('/home/sergio/.openclaw/workspace/denaro/dashboard/fleet_stats.json', 'w') as f:
                json.dump(payload, f, indent=2)
            
            logger.info(f"Matrix Status Synced. Portfolio: {vitals['total_val'] if vitals else '??'} EUR")
            gc.collect()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Automa Error: {e}")
            gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
