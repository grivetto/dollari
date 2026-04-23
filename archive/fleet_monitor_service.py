import gc
import gc
import gc
import os
import json
import time
import logging
import subprocess
from datetime import datetime
from binance.client import Client
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MONITOR] - %(message)s')
logger = logging.getLogger("Monitor")

# Mappa completa di tutti i bot creati
BOT_INVENTORY = {
    "ALPHA_CORE": "binance_bot_multi.py",
    "ALPHA_SURGE": "flash_surge_unit.py",
    "ALPHA_HUNTER": "volatility_hunter.py",
    "ALPHA_SNIPER": "rebound_sniper.py",
    "ALPHA_WAVE": "sergio_wave_rider.py",
    "ALPHA_QUANT": "advanced_quant_bot.py",
    "OMEGA_WARRIOR": "omega_war_machine.py",
    "OMEGA_CENTURION": "centurion_reversion_squad.py",
    "OMEGA_FEEDER": "omega_bottom_feeder.py",
    "OMEGA_REVERSE": "contrarian_omega_squad.py",
    "SIGMA_CHAOS": "sigma_chaos_engine.py",
    "SIGMA_BAIT": "bait_and_trap_engine.py",
    "SYSTEM_ARCHITECT": "architect_ai.py",
    "SYSTEM_EVOLVE": "evolution_engine.py",
    "SYSTEM_AUTOMA": "triad_sentinel_automa.py",
    "SYSTEM_CASH_OUT": "rapid_cash_out.py",
    "TELEGRAM_LINK": "telegram_bot_interactive.py",
    "FUNDING_SNIFFER": "funding_rate_sniffer.py",
    "FLASH_CRASH_ARB": "flash_crash_arbitrageur.py",
    "BOLLINGER": "bollinger_bands_sniper.py",
    "WHALE_TRACKER": "whale_tracker_nano.py"
}

def get_detailed_bot_status():
    ps_output = subprocess.check_output(["ps", "aux"]).decode()
    detailed_status = []
    for display_name, script in BOT_INVENTORY.items():
        is_running = script in ps_output
        detailed_status.append({
            "id": display_name,
            "script": script,
            "status": "ONLINE" if is_running else "OFFLINE",
            "last_check": datetime.now().strftime("%H:%M:%S")
        })
    return detailed_status

def get_market_vitals():
    try:
        load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')
        client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
        prices = client.get_all_tickers()
        btc_price = next(float(p['price']) for p in prices if p['symbol'] == 'BTCEUR')
        
        balances = client.get_account()['balances']
        total_eur = 0.0
        active_assets = []
        
        for b in balances:
            qty = float(b['free']) + float(b['locked'])
            if qty > 0.0001:
                asset = b['asset']
                if asset == 'EUR': total_eur += qty
                elif asset == 'USDT': total_eur += qty
                else:
                    try:
                        p_btc = float(next(p['price'] for p in prices if p['symbol'] == f"{asset}BTC")) if asset != 'BTC' else 1.0
                        val = qty * p_btc * btc_price
                        if val > 1.0:
                            total_eur += val
                            active_assets.append({"name": asset, "val": round(val, 2), "qty": f"{qty:.4f}"})
                    except: pass
        
        return {
            "total_val": round(total_eur, 2),
            "profit": round(total_eur - 722.00, 2),
            "btc_price": btc_price,
            "assets": sorted(active_assets, key=lambda x: x['val'], reverse=True)
        }
    except: return None

def main():
    while True:
        try:
            status = get_detailed_bot_status()
            vitals = get_market_vitals()
            
            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "bot_matrix": status,
                "vitals": vitals
            }
            
            with open('/home/sergio/.openclaw/workspace/denaro/dashboard/fleet_stats.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Full Fleet Monitor Synced. Online: {sum(1 for b in status if b['status'] == 'ONLINE')}/{len(status)}")
            gc.collect()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Monitor Error: {e}")
            gc.collect()
            time.sleep(10)

if __name__ == "__main__":
    main()
