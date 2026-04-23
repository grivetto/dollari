cat << 'HEREDOC' > /home/sergio/autonomous_bot/auto_healer_mc2.py
import os
import glob
import re
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AUTO-HEALER MC2 🛠️] - %(message)s',
                    handlers=[logging.FileHandler("/home/sergio/autonomous_bot/AUTO_HEALER.log"), logging.StreamHandler()])

LOG_DIR = "/home/sergio/autonomous_bot"
VENV_PIP = "/home/sergio/autonomous_bot/venv/bin/pip"

def heal_bots():
    logs = glob.glob(os.path.join(LOG_DIR, "*.log"))
    healed = 0
    
    for log_file in logs:
        bot_name = os.path.basename(log_file).replace(".log", "")
        if bot_name in ["AUTO_HEALER", "watchdog"]:
            continue
            
        try:
            with open(log_file, 'r', errors='ignore') as f:
                content = f.read()
                
            last_lines = content[-3000:]
            if "Traceback" in last_lines or "Exception" in last_lines[-500:]:
                module_match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", last_lines)
                if module_match:
                    missing_module = module_match.group(1)
                    logging.info(f"Rilevato {bot_name} in CRASH per modulo mancante: '{missing_module}'. Avvio auto-installazione...")
                    
                    res = subprocess.run([VENV_PIP, "install", missing_module], capture_output=True, text=True)
                    if res.returncode == 0:
                        logging.info(f"Modulo '{missing_module}' installato con successo! Svuoto il log.")
                        open(log_file, 'w').close()
                        healed += 1
                        continue
                    else:
                        logging.error(f"Fallita installazione: {res.stderr}")
                
                if "NameError: name 'gc' is not defined" in last_lines:
                    logging.info(f"Rilevato {bot_name} in CRASH per 'import gc' mancante. Inietto fix...")
                    script_path = os.path.join(LOG_DIR, bot_name.lower() + ".py")
                    if not os.path.exists(script_path):
                        script_path = os.path.join(LOG_DIR, bot_name + ".py")
                    
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
                            
                mtime = os.path.getmtime(log_file)
                if time.time() - mtime > 3600:
                    logging.info(f"Traceback vecchio in {bot_name} (>1h). Lo azzero.")
                    open(log_file, 'w').close()
                    healed += 1

        except Exception as e:
            pass
            
    if healed > 0:
        subprocess.run(["systemctl", "restart", "bot-watchdog.service"])

if __name__ == "__main__":
    logging.info("Auto-Healer MC2 avviato. Scansione crash in corso...")
    while True:
        heal_bots()
        time.sleep(60)
HEREDOC

cat << 'HEREDOC' > /etc/systemd/system/bot-healer.service
[Unit]
Description=MC2 Auto Healer

[Service]
Type=simple
User=root
WorkingDirectory=/home/sergio/autonomous_bot
ExecStart=/usr/bin/python3 /home/sergio/autonomous_bot/auto_healer_mc2.py
Restart=always

[Install]
WantedBy=multi-user.target
HEREDOC

systemctl daemon-reload
systemctl enable bot-healer.service
systemctl restart bot-healer.service
