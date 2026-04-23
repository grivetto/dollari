import os, time, subprocess
WORKSPACE = "/home/sergio/.openclaw/workspace/denaro"
VENV_PYTHON = f"{WORKSPACE}/trading_bot_env/bin/python3"
for i in range(2, 30):
    script = f"strategies/concept_gen_{i}.py"
    path = os.path.join(WORKSPACE, script)
    if os.path.exists(path):
        try:
            subprocess.Popen([VENV_PYTHON, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Started {script}")
            time.sleep(1)
        except: pass
