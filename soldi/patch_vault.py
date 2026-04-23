import os, glob

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add import fcntl
    if 'import fcntl' not in content:
        content = content.replace('import os, time, logging, gc, json', 'import os, time, logging, gc, json, fcntl')
    
    # Replace get_vault_locked
    old_get = 'def get_vault_locked():\n    try:\n        if os.path.exists(VAULT_FILE):\n            with open(VAULT_FILE, "r") as f:\n                return float(json.load(f).get("LOCKED_EUR", 0.0))\n    except: pass\n    return 0.0'
    new_get = 'def get_vault_locked():\n    try:\n        if os.path.exists(VAULT_FILE):\n            with open(VAULT_FILE, "r") as f:\n                fcntl.flock(f, fcntl.LOCK_SH)\n                val = float(json.load(f).get("LOCKED_EUR", 0.0))\n                fcntl.flock(f, fcntl.LOCK_UN)\n                return val\n    except: pass\n    return 0.0'
    
    # Replace add_to_vault
    # Note: The current code has logger.info(f"⚖️ LEGION MATIC HA VERSATO...") - it's hardcoded per bot.
    # I will use a regex or a block replace to handle the variation in the log message.
    # Since I can't easily regex the hardcoded name, I'll replace the whole function and use the SYMBOL variable.
    
    # This is a bit tricky because the function body differs slightly in the log message.
    # I'll search for the start and end of the function.
    
    import re
    pattern = re.compile(r'def add_to_vault\(amount\):.*?except: pass', re.DOTALL)
    
    new_add = 'def add_to_vault(amount):\n    try:\n        with open(VAULT_FILE, "r+") as f:\n            fcntl.flock(f, fcntl.LOCK_EX)\n            data = json.load(f)\n            locked = data.get("LOCKED_EUR", 0.0) + amount\n            data["LOCKED_EUR"] = locked\n            f.seek(0)\n            json.dump(data, f)\n            f.truncate()\n            fcntl.flock(f, fcntl.LOCK_UN)\n        logger.info(f"⚖️ LEGION {SYMBOL} HA VERSATO: +{amount:.2f}€ IN CASSAFORTE!")\n    except Exception as e:\n        logger.error(f"Errore vault: {e}")'
    
    content = pattern.sub(new_add, content)
    content = content.replace(old_get, new_get)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f'Patched {filepath}')

for f in glob.glob('/home/sergio/denaro/legion_*.py'): patch_file(f)
for f in glob.glob('/home/sergio/denaro/soldi/legion_*.py'): patch_file(f)
