#!/bin/bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv

cd /home/ubuntu/workspace/denaro/
python3 -m venv trading_bot_env
./trading_bot_env/bin/pip install ccxt python-dotenv requests psutil ta

# Create the Tokyo Guardian (only runs Squadra Delta & Whale trackers)
cat << 'PY_EOF' > tokyo_guardian.py
import os, time, subprocess, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', handlers=[logging.FileHandler("/home/ubuntu/workspace/denaro/tokyo_guardian.log")])
logger = logging.getLogger("TokyoGuardian")

WORKSPACE = "/home/ubuntu/workspace/denaro"

BOT_REGISTRY = {
    "SQUADRA_DELTA": "squadra_delta_orderflow.py",
    "WHALE_TRACKER": "whale_tracker_nano.py",
    "TSUNAMI": "tsunami_rider.py",
    "WHALE_MONITOR": "whale_monitor.py"
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
    logger.info("🗼 TOKYO GUARDIAN ONLINE: Order Flow Frontrunner Asiatico")
    while True:
        for name, script in BOT_REGISTRY.items():
            if not is_running(script):
                logger.info(f"{name} is not running, starting...")
                start_bot(name, script)
        time.sleep(10)

if __name__ == "__main__":
    main()
PY_EOF

# Setup systemd service
sudo bash -c "cat << 'SERVICE_EOF' > /etc/systemd/system/tokyo-guardian.service
[Unit]
Description=Tokyo Guardian (HFT Asian Node)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/workspace/denaro
ExecStart=/home/ubuntu/workspace/denaro/trading_bot_env/bin/python3 /home/ubuntu/workspace/denaro/tokyo_guardian.py
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF"

sudo systemctl daemon-reload
sudo systemctl enable tokyo-guardian
sudo systemctl restart tokyo-guardian

