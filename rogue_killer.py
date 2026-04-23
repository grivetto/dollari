import os, time, logging
from lite_guardian import BOT_REGISTRY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ROGUE KILLER 🧹] - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/AUTO_HEALER.log")])

ALLOWED_SCRIPTS = list(BOT_REGISTRY.values()) + [
    "lite_guardian.py", "heavy_guardian.py", "rogue_killer.py", "auto_healer.py", "update_bot_status.py", "update_cache.py", "telegram_bot_interactive.py", "generate_monitoring.py", "midnight_sweeper.py", "hourly_reporter.py", "ai_risk_engine.py", "mev_sandwich_bot.py", "auto_healer_mc2.py", "auto_healer_mc3.py"
]

def scan_and_destroy():
    try:
        ps_output = os.popen("ps aux | grep python").read().split('\n')
        killed = 0
        for line in ps_output:
            if "workspace/denaro/" in line and "grep" not in line and "rogue_killer" not in line:
                parts = line.split()
                pid = parts[1]
                # Find the script name from the full command string
                script_name = None
                for part in parts:
                    if ".py" in part and "denaro" in part:
                        script_name = part.split('/')[-1]
                        break
                
                if script_name and script_name not in ALLOWED_SCRIPTS:
                    logging.warning(f"Rilevato processo ZOMBIE/NON AUTORIZZATO: {script_name} (PID: {pid}). TERMINAZIONE IN CORSO...")
                    os.system(f"kill -9 {pid}")
                    killed += 1
        return killed
    except Exception as e:
        logging.error(f"Errore scanner Rogue Killer: {e}")
        return 0

if __name__ == "__main__":
    logging.info("Rogue Killer Inizializzato. Scansione attiva...")
    while True:
        killed = scan_and_destroy()
        if killed > 0:
            logging.info(f"Pulizia completata. {killed} processi parassiti eliminati.")
        time.sleep(300) # Scansiona ogni 5 minuti
