import os, json, fcntl, logging

VAULT_FILE = '/home/sergio/denaro/vault.json'

def read_vault():
    try:
        if not os.path.exists(VAULT_FILE): return {}
        with open(VAULT_FILE, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
            return data
    except Exception as e:
        logging.error(f'Error reading vault: {e}')
        return {}

def write_vault(data):
    try:
        with open(VAULT_FILE, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=4)
            fcntl.flock(f, fcntl.LOCK_UN)
        return True
    except Exception as e:
        logging.error(f'Error writing vault: {e}')
        return False
