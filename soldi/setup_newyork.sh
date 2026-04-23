#!/bin/bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv

cd /home/ubuntu/workspace/denaro/
python3 -m venv trading_bot_env
./trading_bot_env/bin/pip install ccxt python-dotenv requests psutil ta bs4 lxml

# Create the New York Guardian
cat << 'PY_EOF' > newyork_guardian.py
import os, time, subprocess, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.FileHandler("/home/ubuntu/workspace/denaro/newyork_guardian.log")])
logger = logging.getLogger("NYGuardian")

WORKSPACE = "/home/ubuntu/workspace/denaro"

BOT_REGISTRY = {
    "SQUADRA_ALPHA": "alpha_strike_scalper.py",
    "NEWS_SNIPER": "news_sentiment_sniper.py",
    "AUTO_HEALER": "auto_healer_ny.py"
}

def is_running(script):
    try:
        base_name = os.path.basename(script)
        out = subprocess.check_output(["pgrep", "-f", f"python.*{base_name}"])
        return True
    except: return False

def start_bot(name, script):
    path = os.path.join(WORKSPACE, script)
    if not os.path.exists(path): return
    try:
        subprocess.Popen(["/home/ubuntu/workspace/denaro/trading_bot_env/bin/python3", path], stdout=open(f"{WORKSPACE}/{name}.log", "a"), stderr=subprocess.STDOUT, cwd=WORKSPACE)
        logger.info(f"Started {name}")
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")

def main():
    logger.info("🗽 NEW YORK GUARDIAN ONLINE: Macro Trader & News Sniper Wall Street")
    while True:
        for name, script in BOT_REGISTRY.items():
            if not is_running(script):
                logger.info(f"{name} is not running, starting...")
                start_bot(name, script)
        time.sleep(10)

if __name__ == "__main__":
    main()
PY_EOF

# Create the Auto Healer for NY
cat << 'PY_EOF' > auto_healer_ny.py
import os, glob, re, subprocess, logging, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AUTO-HEALER NY 🛠️] - %(message)s',
                    handlers=[logging.FileHandler("/home/ubuntu/workspace/denaro/AUTO_HEALER.log")])

LOG_DIR = "/home/ubuntu/workspace/denaro"
VENV_PIP = "/home/ubuntu/workspace/denaro/trading_bot_env/bin/pip"

def heal_bots():
    logs = glob.glob(os.path.join(LOG_DIR, "*.log"))
    healed = 0
    for log_file in logs:
        bot_name = os.path.basename(log_file).replace(".log", "")
        if bot_name in ["AUTO_HEALER", "newyork_guardian"]: continue
        try:
            with open(log_file, 'r', errors='ignore') as f:
                content = f.read()
            last_lines = content[-3000:]
            if "Traceback" in last_lines or "Exception" in last_lines[-500:]:
                m = re.search(r"ModuleNotFoundError: No module named '([^']+)'", last_lines)
                if m:
                    module = m.group(1)
                    res = subprocess.run([VENV_PIP, "install", module], capture_output=True)
                    if res.returncode == 0:
                        open(log_file, 'w').close()
                        healed += 1
                        continue
                if "NameError: name 'gc' is not defined" in last_lines:
                    script_path = os.path.join(LOG_DIR, bot_name.lower() + ".py")
                    if not os.path.exists(script_path): script_path = os.path.join(LOG_DIR, bot_name + ".py")
                    if os.path.exists(script_path):
                        with open(script_path, 'r') as sf: sc = sf.read()
                        if "import gc" not in sc:
                            with open(script_path, 'w') as sf: sf.write("import gc\n" + sc)
                            open(log_file, 'w').close()
                            healed += 1
                            continue
                mtime = os.path.getmtime(log_file)
                if time.time() - mtime > 3600:
                    open(log_file, 'w').close()
                    healed += 1
        except: pass
    if healed > 0:
        subprocess.run(["sudo", "systemctl", "restart", "newyork-guardian.service"])

if __name__ == "__main__":
    while True:
        heal_bots()
        time.sleep(60)
PY_EOF

# Setup systemd service
sudo bash -c "cat << 'SERVICE_EOF' > /etc/systemd/system/newyork-guardian.service
[Unit]
Description=New York Guardian (News Node)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/workspace/denaro
ExecStart=/home/ubuntu/workspace/denaro/trading_bot_env/bin/python3 /home/ubuntu/workspace/denaro/newyork_guardian.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF"

sudo systemctl daemon-reload
sudo systemctl enable newyork-guardian
sudo systemctl restart newyork-guardian

