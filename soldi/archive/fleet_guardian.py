import gc
import os, time, subprocess, logging

LOG_FILE = "/home/sergio/.openclaw/workspace/denaro/fleet_guardian.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.FileHandler(LOG_FILE)])
logger = logging.getLogger("Guardian")

WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"
VENV_PYTHON = f"{WORKSPACE}/trading_bot_env/bin/python3"
SYSTEM_PYTHON = "/usr/bin/python3"

BOT_REGISTRY = {
    "SNIPER-SQUAD": "sniper_squad.py",
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
    "ZABBIX-WATCHDOG": "zabbix_watchdog.py",
    "FLASH-CATCHER": "flash_catcher.py",
    "RSI-HUNTER": "rsi_divergence_hunter.py",
    "FUNDING-SNIFFER": "funding_rate_sniffer.py",
    "FLASH-CRASH-ARB": "flash_crash_arbitrageur.py",
    "VWAP-SNIPER": "vwap_reversion_sniper.py",
    "ZERO-OOM-SCALPER": "zero_oom_scalper.py",
    "MICRO-FLASH-CRASH": "micro_flash_crash_scalper.py",
    "NEON-ZERO": "neon_sniper_zero.py",
    "MICRO-TREND": "micro_trend_tracker.py",
    "FLEET-REPORTER": "fleet_reporter.py",
    "MICRO-FRACTOR": "micro_fractor_bot.py"
}

def is_running(script):
    try:
        base_name = os.path.basename(script)
        out = subprocess.check_output("ps aux", shell=True).decode()
        for line in out.splitlines():
            if base_name in line and "python" in line and "fleet_guardian" not in line and "fleet_reporter" not in line:
                return True
        return False
    except: return False

def start_bot(name, script):
    py = VENV_PYTHON if os.path.exists(VENV_PYTHON) else SYSTEM_PYTHON
    
    # Handle dashboard server parameters specially
    if script == "dashboard_server.py":
        path = os.path.join(WORKSPACE, "dashboard", script)
        cmd = [py, path, "8080"]
    else:
        path = os.path.join(WORKSPACE, script)
        cmd = [py, path]
        
    if not os.path.exists(path): 
        logger.error(f"Path non trovato: {path}")
        return
        
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=WORKSPACE)
        logger.info(f"Started {name} ({script})")
    except Exception as e: 
        logger.error(f"Failed to start {name}: {e}")

def main():
    logger.info("🛡️ GUARDIAN 5.0: Fleet 5 Min Auto-Check Booted")
    import gc
    while True:
        gc.collect()
        try:
            for name, script in BOT_REGISTRY.items():
                if not is_running(script):
                    start_bot(name, script)
                    time.sleep(2) 
        except Exception as e:
            logger.error(f"Guardian error: {e}")
        
        # Dorme 5 minuti
        time.sleep(300)

if __name__ == "__main__":
    main()
