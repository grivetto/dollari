import gc
import os, json, time, subprocess
from datetime import datetime

STATUS_PATH = "/home/sergio/.openclaw/workspace/denaro/dashboard/fleet_stats.json"

BOTS = {
    "SNIPER-SQUAD": "sniper_squad.py",
    "VAULT-MANAGER": "vault_manager.py",
    "TG-BOT": "telegram_bot_interactive.py",
    "DASHBOARD": "dashboard_server.py",
    "GARIBAN-BEGGAR": "gariban_beggar.py",
    "VAMPIRE-GRID": "vampire_grid.py",
    "SCAVENGER": "scavenger_doge.py",
    "PHANTOM-MAKER": "phantom_maker.py",
    "TSUNAMI-RIDER": "tsunami_rider.py",
    "HUNTER-SWARM": "hunter_swarm.py",
    "DARKPOOL-ARB": "dark_pool_arb.py",
    "BLACKHOLE-ABS": "black_hole_absorber.py",
    "STABLE-SCALPER": "stable_scalper.py",
    "ORDERBOOK-SNIPER": "orderbook_imbalance_sniper.py",
    "MICRO-FLASH-CRASH": "micro_flash_crash_scalper.py",
    "ZABBIX-WATCHDOG": "zabbix_watchdog.py",
    "FLASH-CATCHER": "flash_catcher.py",
    "RSI-HUNTER": "rsi_divergence_hunter.py",
    "FUNDING-SNIFFER": "funding_rate_sniffer.py",
    "FLASH-CRASH-ARB": "flash_crash_arbitrageur.py",
    "VWAP-SNIPER": "vwap_reversion_sniper.py",
    "ZERO-OOM-SCALPER": "zero_oom_scalper.py",
    "NEON-ZERO": "neon_sniper_zero.py",
    "MICRO-TREND": "micro_trend_tracker.py"
}

def main():
    import gc
    while True:
        gc.collect()
        status = {}
        try:
            ps = subprocess.check_output(["ps", "aux"]).decode()
            
            # Controllo manuale logica vault da sniper squad se non c'è vault manager
            sniper_running = "sniper_squad.py" in ps
            
            for n, s in BOTS.items():
                base_name = os.path.basename(s)
                on = base_name in ps
                
                # Se sniper squad è in esecuzione, il vault 33% è in esecuzione (integrato nel codice)
                if n == "VAULT-MANAGER" and sniper_running:
                    on = True
                    s = "integrato in sniper_squad"

                status[n] = {
                    "status": "ONLINE" if on else "OFFLINE", 
                    "script": s, 
                    "last_seen": datetime.now().strftime("%H:%M:%S") if on else "N/A"
                }
            
            with open(STATUS_PATH, "w") as f:
                json.dump({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "fleet": status}, f, indent=2)
        except Exception as e: 
            print("Errore", e)
        time.sleep(15)

if __name__ == "__main__":
    main()
