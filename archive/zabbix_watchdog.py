import gc
import os, time, logging, subprocess, json, gc
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/ZABBIX.log"), logging.StreamHandler()])
logger = logging.getLogger("Zabbix")

WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"
METRICS_FILE = os.path.join(WORKSPACE, "dashboard", "zabbix_metrics.json")
HISTORY_FILE = os.path.join(WORKSPACE, "zabbix_history.json")

BOTS = {
    "SNIPER_SQUAD": "sniper_squad.py",
    "GARIBAN": "gariban_beggar.py",
    "VAMPIRO": "vampire_grid.py",
    "SCIACALLO": "scavenger_doge.py",
    "PHANTOM": "phantom_maker.py",
    "TSUNAMI": "tsunami_rider.py",
    "SCIAME": "hunter_swarm.py",
    "DARKPOOL": "dark_pool_arb.py",
    "BLACKHOLE": "black_hole_absorber.py",
    "STABLESCALP": "stable_scalper.py",
    "FLASH_CATCHER": "flash_catcher.py",
    "RSI_HUNTER": "rsi_divergence_hunter.py",
    "ALPHA_STRIKE": "alpha_strike_scalper.py",
    "MEV_BRAIN": "mev_sandwich_bot.py",
    "DELTA_HEDGE": "delta_neutral_hedge.py",
    "ASIAN_ECHO": "spatial_arbitrageur.py",
    "NEWS_SNIPER": "news_sentiment_sniper.py",
    "KNIFE_SNIPER": "dumping_knife_sniper.py",
    "FUND_ARB": "funding_arbitrage_estremo.py",
    "OLYMPUS": "olympus_grid_binance.py",

    "TG_BOT": "telegram_bot_interactive.py",
    "DASHBOARD": "dashboard_server.py",
    "LEGION_ADA": "legion_01_ada.py",
    "LEGION_AVAX": "legion_02_avax.py",
    "LEGION_LINK": "legion_03_link.py",
    "LEGION_MATIC": "legion_04_matic.py",
    "LEGION_DOT": "legion_05_dot.py",
    "LEGION_UNI": "legion_06_uni.py",
    "LEGION_LTC": "legion_07_ltc.py",
    "LEGION_ATOM": "legion_08_atom.py",
    "LEGION_ETC": "legion_09_etc.py",
    "LEGION_XLM": "legion_10_xlm.py",
    "LEGION_BCH": "legion_11_bch.py",
    "LEGION_ALGO": "legion_12_algo.py",
    "LEGION_VET": "legion_13_vet.py",
    "LEGION_FIL": "legion_14_fil.py",
    "LEGION_AAVE": "legion_15_aave.py",
    "LEGION_EOS": "legion_16_eos.py",
    "LEGION_XTZ": "legion_17_xtz.py",
    "LEGION_MANA": "legion_18_mana.py",
    "LEGION_SAND": "legion_19_sand.py",
    "LEGION_AXS": "legion_20_axs.py",
    "LEGION_GALA": "legion_21_gala.py",
    "LEGION_ENJ": "legion_22_enj.py",
    "LEGION_CHZ": "legion_23_chz.py",
    "LEGION_ZIL": "legion_24_zil.py",
    "LEGION_BAT": "legion_25_bat.py",
    "LEGION_MKR": "legion_26_mkr.py",
    "LEGION_NEAR": "legion_27_near.py",
    "LEGION_FTM": "legion_28_ftm.py"
}

def get_process_info(script_name):
    try:
        out = subprocess.check_output(f"ps aux | grep '{script_name}' | grep -v grep || true", shell=True).decode().strip()
        if not out: return None
        lines = out.split('\n')
        # Return sum of cpu/mem if multiple
        total_cpu = 0.0
        total_mem = 0.0
        pid = lines[0].split()[1] # take first pid
        for l in lines:
            parts = l.split()
            if len(parts) >= 4:
                total_cpu += float(parts[2])
                total_mem += float(parts[3])
                
        return {
            "pid": pid,
            "cpu": total_cpu,
            "mem": total_mem
        }
    except:
        return None

def main():
    logger.info("👁️ ZABBIX WATCHDOG AVVIATO. Monitoraggio Salute Server e OOM Prevention.")
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except: pass

    while True:
        try:
            metrics = {}
            total_cpu = 0.0
            total_mem = 0.0
            
            for name, script in BOTS.items():
                info = get_process_info(script)
                
                # Resolving correct log paths
                if name == "SNIPER_SQUAD": log_name = "sniper_squad.log"
                elif name == "GARIBAN": log_name = "GARIBAN.log"
                elif name == "VAMPIRO": log_name = "VAMPIRE.log"
                elif name == "SCIACALLO": log_name = "SCAVENGER.log"
                elif name == "PHANTOM": log_name = "PHANTOM.log"
                elif name == "TSUNAMI": log_name = "TSUNAMI.log"
                elif name == "SCIAME": log_name = "HUNTER_SWARM.log"
                elif name == "DARKPOOL": log_name = "DARKPOOL.log"
                elif name == "BLACKHOLE": log_name = "BLACKHOLE.log"
                elif name == "STABLESCALP": log_name = "STABLE_SCALPER.log"
                elif name == "RSI_HUNTER": log_name = "RSI_HUNTER.log"
                elif name == "TG_BOT": log_name = "TG-BOT.log"
                elif name == "DASHBOARD": log_name = "DASHBOARD.log"
                elif name.startswith('LEGION_'): log_name = f"{name}.log"
                else: log_name = f"{name}.log"
                
                log_path = os.path.join(WORKSPACE, log_name)
                
                status = "OFFLINE"
                last_log_sec = 0
                
                if info:
                    status = "ONLINE"
                    total_cpu += info["cpu"]
                    total_mem += info["mem"]
                    
                    if os.path.exists(log_path):
                        last_log_sec = time.time() - os.path.getmtime(log_path)
                        # Zombie if no log update in 15 minutes (900 seconds) AND log exists
                        if last_log_sec > 600 and not name.startswith("LEGION") and name not in ["TG_BOT", "DASHBOARD", "YIELD_FARMER", "LITE_GUARDIAN"]:
                            status = "ZOMBIE"
                            logger.warning(f"🧟 {name} IN STATO ZOMBIE! Log bloccato da {last_log_sec:.0f}s. UCCISIONE IN CORSO PID {info['pid']}!")
                            os.system(f"kill -9 {info['pid']}")
                            info = None
                            status = "KILLED"
                
                metrics[name] = {
                    "status": status,
                    "cpu": round(info["cpu"], 1) if info else 0.0,
                    "mem": round(info["mem"], 1) if info else 0.0,
                    "pid": info["pid"] if info else "---",
                    "log_age_s": round(last_log_sec) if info else 0
                }
                
            now_str = datetime.now().strftime("%H:%M")
            
            history.append({
                "time": now_str,
                "cpu": round(total_cpu, 2),
                "mem": round(total_mem, 2)
            })
            
            if len(history) > 60: history = history[-60:]
                
            try:
                with open(HISTORY_FILE, 'w') as f:
                    json.dump(history, f)
            except: pass
                
            try:
                with open(METRICS_FILE, 'w') as f:
                    json.dump({"timestamp": now_str, "bots": metrics, "history": history}, f)
            except: pass
            
            # Watchdog frequency 1 min
            time.sleep(60)
            gc.collect()
            
        except Exception as e:
            logger.error(f"Errore Watchdog: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
