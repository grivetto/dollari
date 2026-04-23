import os
import glob
import re
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AUTO-HEALER 🛠️] - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/.openclaw/workspace/denaro/AUTO_HEALER.log"), logging.StreamHandler()])

LOG_DIR = "/home/sergio/.openclaw/workspace/denaro"
VENV_PIP = "/home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/pip"

def heal_bots():
    logs = glob.glob(os.path.join(LOG_DIR, "*.log"))
    healed = 0
    
    for log_file in logs:
        bot_name = os.path.basename(log_file).replace(".log", "")
        if bot_name in ["AUTO_HEALER", "DASHBOARD_WEB", "DASHBOARD", "DEFCON", "CACHE_UPD", "WATCHDOG", "AI_RISK", "bot_execution", "nuvola_quant_bot", "openclaw", "bot_ctl", "lite_guardian", "monitoraggio_fiammate", "bot_evolution", "trading_bot_aggressive", "whale_monitor", "sentinel_trend"]:
            continue
            
        try:
            with open(log_file, 'r', errors='ignore') as f:
                content = f.read()
                
            last_lines = content[-3000:]
            if "Traceback" in last_lines or "Exception" in last_lines[-500:]:
                # We found a crash!
                # 1. Check for ModuleNotFoundError
                module_match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", last_lines)
                if module_match:
                    missing_module = module_match.group(1)
                    logging.info(f"Rilevato {bot_name} in CRASH per modulo mancante: '{missing_module}'. Avvio auto-installazione...")
                    
                    # Install it
                    res = subprocess.run([VENV_PIP, "install", missing_module], capture_output=True, text=True)
                    if res.returncode == 0:
                        logging.info(f"Modulo '{missing_module}' installato con successo! Svuoto il log per forzare il riavvio pulito.")
                        open(log_file, 'w').close()
                        healed += 1
                        continue
                    else:
                        logging.error(f"Fallita installazione di '{missing_module}': {res.stderr}")
                
                # 2. Check for NameError: name 'gc' is not defined
                if "NameError: name 'gc' is not defined" in last_lines:
                    logging.info(f"Rilevato {bot_name} in CRASH per 'import gc' mancante. Inietto fix...")
                    script_path = os.path.join(LOG_DIR, bot_name + ".py")
                    
                    # Some log names are uppercase, script names lowercase. Let's try to find the script
                    if not os.path.exists(script_path):
                        script_path = os.path.join(LOG_DIR, bot_name.lower() + ".py")
                    
                    if os.path.exists(script_path):
                        with open(script_path, 'r') as sf:
                            script_code = sf.read()
                        if "import gc" not in script_code:
                            with open(script_path, 'w') as sf:
                                sf.write("import gc\n" + script_code)
                            logging.info(f"Riparato script {os.path.basename(script_path)}. Svuoto log.")
                            open(log_file, 'w').close()
                            healed += 1
                            continue
                            
                # 3. Handle Generic Crash Loops by clearing the log if it's very old, or waiting for Lite Guardian
                # If there's a Traceback but no known quick-fix, we can't heal it perfectly yet without an LLM call.
                # Let's at least clear the log if it's older than 1 hour to see if it recurs.
                mtime = os.path.getmtime(log_file)
                if time.time() - mtime > 3600:
                    logging.info(f"Traceback vecchio in {bot_name} (>1h). Lo azzero per vedere se il crash è risolto.")
                    open(log_file, 'w').close()
                    healed += 1

        except Exception as e:
            pass
            
    if healed > 0:
        subprocess.run(["sudo", "systemctl", "restart", "denaro-lite-guardian.service"])

if __name__ == "__main__":
    logging.info("Auto-Healer avviato. Scansione crash in corso...")
    while True:
        heal_bots()
        time.sleep(60)

