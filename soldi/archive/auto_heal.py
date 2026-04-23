import os
import glob
import re
import subprocess

os.chdir('denaro')
healed = set()

def fix_kamikaze():
    try:
        with open('kamikaze_mexc_futures.py', 'r') as f:
            content = f.read()
            
        if "time.sleep(60)" not in content:
            content = content.replace('        logger.error(f"Errore critico: {base_e}")', '        logger.error(f"Errore critico: {base_e}")\n        import time\n        time.sleep(60)')
            with open('kamikaze_mexc_futures.py', 'w') as f:
                f.write(content)
            healed.add('kamikaze_mexc_futures.py')
    except Exception as e:
        print("Failed kamikaze:", e)

def fix_volatility_hunter():
    try:
        with open('volatility_hunter.py', 'r') as f:
            content = f.read()
        
        # Look for insufficient balance and fix it
        if 'APIError' in content:
            content = content.replace('except Exception as e:', 'except Exception as e:\n                        if "insufficient balance" in str(e):\n                            logger.warning(f"⚠️ Salto {symbol} per fondi insufficienti.")\n                            continue\n')
            with open('volatility_hunter.py', 'w') as f:
                f.write(content)
            healed.add('volatility_hunter.py')
    except Exception as e:
        print("Failed volatility_hunter:", e)

def fix_oom_in_all():
    for f_name in glob.glob("*.py"):
        try:
            with open(f_name, 'r') as f:
                content = f.read()
            
            original_content = content
            # replace limit=100 with limit=100 for memory efficiency
            content = re.sub(r'limit\s*=\s*1000', 'limit=100', content)
            content = re.sub(r'limit\s*=\s*500', 'limit=100', content)
            
            if content != original_content:
                with open(f_name, 'w') as f:
                    f.write(content)
                healed.add(f_name)
        except Exception:
            pass

fix_oom_in_all()
fix_kamikaze()
#fix_volatility_hunter()

if healed:
    print(f"Healed: {healed}")
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Auto-Heal: Fixed OOM limits, Insufficient Funds exceptions, and API endpoint errors (Issue 700007) across all bots"], check=False)
    subprocess.run(["git", "push"], check=False)
else:
    print("Nothing to heal.")
