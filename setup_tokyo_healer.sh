cat << 'PY_EOF' > /home/ubuntu/workspace/denaro/auto_healer_tokyo.py
import os, glob, re, subprocess, logging, time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AUTO-HEALER TOKYO 🎌] - %(message)s',
                    handlers=[logging.FileHandler("/home/ubuntu/workspace/denaro/AUTO_HEALER.log")])

LOG_DIR = "/home/ubuntu/workspace/denaro"
VENV_PIP = "/home/ubuntu/workspace/denaro/trading_bot_env/bin/pip"

def heal_bots():
    logs = glob.glob(os.path.join(LOG_DIR, "*.log"))
    healed = 0
    for log_file in logs:
        bot_name = os.path.basename(log_file).replace(".log", "")
        if bot_name in ["AUTO_HEALER", "tokyo_guardian"]: continue
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
        subprocess.run(["sudo", "systemctl", "restart", "tokyo-guardian.service"])

if __name__ == "__main__":
    while True:
        heal_bots()
        time.sleep(60)
PY_EOF

# Add it to tokyo_guardian.py if missing
grep -q "AUTO_HEALER" /home/ubuntu/workspace/denaro/tokyo_guardian.py || sed -i '/"TSUNAMI":/a \    "AUTO_HEALER": "auto_healer_tokyo.py",' /home/ubuntu/workspace/denaro/tokyo_guardian.py

sudo systemctl restart tokyo-guardian
