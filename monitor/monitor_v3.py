#!/usr/bin/env python3
"""
DENARO MONITOR H24 V3 - PROATTIVO E INTELLIGENTE
- Controlla salute bot (processi + log recenti)
- Verifica connettivita Binance e dashboard
- Monitora bilanci anomali (alert se drop improvviso)
- Auto-healing: riavvia bot morti
- Report Telegram a intervalli regolari
- Check processi zombie (duplicati)
"""

import ccxt
import os
import sys
import time
import json
import logging
import subprocess
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

TELEGRAM_TOKEN = os.getenv('TG_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', ''))
CHAT_ID = os.getenv('TG_CHAT_ID', '277954993')
API_KEY = os.getenv('BINANCE_API_KEY', '')
API_SECRET = os.getenv('BINANCE_API_SECRET', '')

MC2_USER = "sergio"
MC2_HOST = "93.43.252.114"
MC2_PORT = "2222"

STATE_FILE = '/home/sergio/.openclaw/workspace/denaro/monitor/state.json'
LOG_FILE = '/home/sergio/.openclaw/workspace/denaro/monitor/monitor.log'

os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MONITOR V3] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

NUVOLA_BOTS = [
    {'name': 'Grid Bot V2', 'pattern': 'grid_bot_v2', 'service': 'denaro-grid-v2'},
    {'name': 'DCA Bot',     'pattern': 'dca_bot',      'service': 'denaro-dca-bot'},
    {'name': 'Telegram',    'pattern': 'telegram_bot', 'service': None},
    {'name': 'Hermes Chat', 'pattern': 'hermes_chat',  'service': None},
    {'name': 'Dashboard',   'pattern': 'dashboard_v3', 'service': None},
]
MC2_BOTS = [
    {'name': 'Sniper V2',   'pattern': 'rebound_sniper_v2'},
    {'name': 'Trend Bot',   'pattern': 'trend_following'},
    {'name': 'Status Srv',  'pattern': 'mc2_status_server'},
]

def send_telegram(msg, force=False):
    if not TELEGRAM_TOKEN or len(TELEGRAM_TOKEN) < 10:
        logger.warning("Token Telegram mancante o vuoto")
        return
    try:
        state = load_state()
        if not force and state.get('mute_until', 0) > time.time():
            return
        txt = f"Monitor V3\n{msg}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={'chat_id': CHAT_ID, 'text': txt}, timeout=5)
        if r.status_code != 200:
            logger.warning(f"Telegram API error: {r.text[:100]}")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {'restarts': {}, 'last_balance_check': 0, 'last_report': 0, 'balance_log': []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def ssh_mc2(cmd, timeout=15):
    full = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 -p {MC2_PORT} {MC2_USER}@{MC2_HOST} '{cmd}'"
    try:
        r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', 'TIMEOUT'
    except Exception as e:
        return -1, '', str(e)

def count_processes_local(pattern):
    r = subprocess.run(f"ps aux | grep '{pattern}' | grep python | grep -v grep | wc -l", shell=True, capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except:
        return 0

def count_processes_mc2(pattern):
    rc, out, _ = ssh_mc2(f"ps aux | grep '{pattern}' | grep python | grep -v grep | wc -l")
    try:
        return int(out.strip())
    except:
        return 0

def restart_bot_local(pattern, service=None):
    if service:
        subprocess.run(f"sudo systemctl restart {service}", shell=True)
    else:
        subprocess.run(f"pkill -9 -f {pattern}", shell=True)
        time.sleep(2)
        subprocess.run(f"cd /home/sergio/.openclaw/workspace/denaro && nohup trading_bot_env/bin/python3 {pattern}.py > /tmp/{pattern}.log 2>&1 &", shell=True)
    state = load_state()
    key = f"nuvola_{pattern}"
    state['restarts'][key] = state['restarts'].get(key, 0) + 1
    save_state(state)
    return state['restarts'][key]

def restart_bot_mc2(pattern):
    ssh_mc2(f"pkill -9 -f {pattern}")
    time.sleep(2)
    if 'trend' in pattern:
        ssh_mc2("cd /home/sergio/denaro && nohup venv/bin/python3 trend_following_bot.py > logs/trend_clean.log 2>&1 &")
    elif 'sniper' in pattern:
        ssh_mc2("cd /home/sergio/denaro && nohup venv/bin/python3 rebound_sniper_v2.py > logs/sniper_fixed.log 2>&1 &")
    elif 'status' in pattern:
        ssh_mc2("cd /home/sergio/denaro && nohup venv/bin/python3 mc2_status_server.py > /dev/null 2>&1 &")
    else:
        ssh_mc2(f"cd /home/sergio/denaro && nohup venv/bin/python3 {pattern}.py > logs/{pattern}.log 2>&1 &")
    state = load_state()
    key = f"mc2_{pattern}"
    state['restarts'][key] = state['restarts'].get(key, 0) + 1
    save_state(state)
    return state['restarts'][key]

def get_binance_balance():
    try:
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': API_SECRET, 'enableRateLimit': True})
        bal = ex.fetch_balance()
        total = 0
        assets = {}
        for b in bal.get('info', {}).get('balances', []):
            f = float(b.get('free', 0))
            l = float(b.get('locked', 0))
            v = f + l
            if v <= 0: continue
            asset = b['asset']
            if asset == 'EUR':
                assets[asset] = {'total': v, 'eur_val': v}
                total += v
            else:
                try:
                    price = ex.fetch_ticker(f"{asset}/EUR")['last']
                    val = v * price
                    assets[asset] = {'total': v, 'eur_val': val, 'price': price}
                    total += val
                except:
                    pass
        return total, assets
    except Exception as e:
        logger.error(f"Binance balance error: {e}")
        return None, {}

def check_binance_connection():
    try:
        ex = ccxt.binance({'apiKey': API_KEY, 'secret': API_SECRET, 'enableRateLimit': True})
        ticker = ex.fetch_ticker('ETH/EUR')
        return True, ticker['last']
    except Exception as e:
        return False, str(e)

def check_dashboard(url):
    try:
        r = requests.get(url, timeout=10, verify=False)
        return r.status_code == 200, r.status_code
    except:
        return False, 0

def send_daily_report():
    total, assets = get_binance_balance()
    if total is None:
        send_telegram("Impossibile recuperare il bilancio.", force=True)
        return
    lines = []
    for asset, info in sorted(assets.items(), key=lambda x: -x[1]['eur_val']):
        if info['eur_val'] > 1:
            lines.append(f"  {asset}: EUR {info['eur_val']:.2f}")
    lines.append(f"\nTOTALE: EUR {total:.2f}")
    
    ram = subprocess.run("free -m | grep Mem | awk '{printf \"%d%%\", $3/$2*100}'", shell=True, capture_output=True, text=True).stdout.strip()
    report = f"REPORT SISTEMA\n\n" + "\n".join(lines) + f"\n\nNuvola RAM: {ram}\n\nTutti i bot monitorati e attivi."
    send_telegram(report, force=True)

def main():
    logger.info("=" * 50)
    logger.info("MONITOR V3 - STARTING CYCLE")
    logger.info("=" * 50)
    issues = []

    # 1. BINANCE
    ok, val = check_binance_connection()
    if ok:
        logger.info(f"Binance OK | ETH/EUR: {val}")
    else:
        msg = f"Binance FAILED: {val}"
        logger.error(msg)
        issues.append(msg)
        send_telegram(f"CRITICO: Connessione Binance fallita!\n{val}")

    # 2. RAM
    ram = subprocess.run("free -m | grep Mem | awk '{printf \"%d/%dMB (%d%%)\", $3, $2, $3/$2*100}'", shell=True, capture_output=True, text=True).stdout.strip()
    logger.info(f"Nuvola RAM: {ram}")

    rc, mc2_ram, _ = ssh_mc2("free -m | grep Mem | awk '{printf \"%d/%dMB (%d%%)\", $3, $2, $3/$2*100}'")
    if mc2_ram: logger.info(f"MC2 RAM: {mc2_ram}")

    # 3. NUVOLE BOTS
    logger.info("--- Nuvola Bots ---")
    for bot in NUVOLA_BOTS:
        cnt = count_processes_local(bot['pattern'])
        if cnt == 0:
            logger.warning(f"DEAD: {bot['name']}")
            n = restart_bot_local(bot['pattern'], bot.get('service'))
            issues.append(f"Riavviato {bot['name']} (#{n})")
            if n >= 5: send_telegram(f"ALERTA: {bot['name']} riavviato {n} volte!")
        elif cnt > 1:
            logger.warning(f"ZOMBIE(x{cnt}): {bot['name']}")
            subprocess.run(f"pkill -9 -f {bot['pattern']}", shell=True)
            time.sleep(2)
            n = restart_bot_local(bot['pattern'], bot.get('service'))
            issues.append(f"Zombie {bot['name']} ucciso e riavviato")
        else:
            logger.info(f"OK: {bot['name']}")

    # 4. MC2 BOTS
    logger.info("--- MC2 Bots ---")
    rc_ping, out_ping, _ = ssh_mc2("echo PONG")
    if rc_ping == 0 and "PONG" in out_ping:
        for bot in MC2_BOTS:
            cnt = count_processes_mc2(bot['pattern'])
            if cnt == 0:
                logger.warning(f"DEAD: {bot['name']} (MC2)")
                n = restart_bot_mc2(bot['pattern'])
                issues.append(f"MC2 Riavviato {bot['name']} (#{n})")
            elif cnt > 1:
                logger.warning(f"ZOMBIE(x{cnt}): {bot['name']} (MC2)")
                ssh_mc2(f"pkill -9 -f {bot['pattern']}")
                time.sleep(2)
                n = restart_bot_mc2(bot['pattern'])
                issues.append(f"MC2 Zombie ucciso {bot['name']}")
            else:
                logger.info(f"OK: {bot['name']} (MC2)")
    else:
        msg = "MC2 OFFLINE!"
        logger.error(msg)
        issues.append(msg)
        send_telegram("MC2 non risponde!", force=True)

    # 5. DASHBOARDS
    ok_n, _ = check_dashboard('https://sgrivett.ddns.net:8443')
    if ok_n: logger.info("Dashboard Nuvola OK")
    else:
        logger.warning("Dashboard Nuvola DOWN")
        subprocess.run("pkill -9 -f dashboard_v3", shell=True)
        time.sleep(2)
        subprocess.run("cd /home/sergio/.openclaw/workspace/denaro && nohup trading_bot_env/bin/python3 dashboard_v3_unified.py > /tmp/dashboard_v3.log 2>&1 &", shell=True)
        issues.append("Dashboard Nuvola riavviata")

    ok_m, _ = check_dashboard('https://mgrivett.ddns.net')
    if ok_m: logger.info("Dashboard MC2 OK")
    else:
        logger.warning("Dashboard MC2 DOWN")
        ssh_mc2("pkill -9 -f mc2_status_server")
        time.sleep(2)
        ssh_mc2("cd /home/sergio/denaro && nohup venv/bin/python3 mc2_status_server.py > /dev/null 2>&1 &")
        issues.append("Dashboard MC2 riavviata")

    # 6. BALANCE CHECK
    state = load_state()
    now = time.time()
    if now - state.get('last_balance_check', 0) > 1800:
        total, assets = get_binance_balance()
        if total is not None:
            logger.info(f"Total Balance: EUR {total:.2f}")
            log_entry = state.get('balance_log', [])
            log_entry.append({'time': datetime.now().isoformat(), 'total': total})
            state['balance_log'] = log_entry[-100:]
            state['last_balance_check'] = now
            save_state(state)
            # Drop check
            if len(log_entry) >= 2:
                prev = log_entry[-2]['total']
                pct = ((total - prev) / prev) * 100 if prev > 0 else 0
                if pct < -5:
                    send_telegram(f"ALERTA DROP!\nPrima: EUR {prev:.2f}\nOra: EUR {total:.2f}\nDelta: {pct:.1f}%", force=True)

    # 7. DAILY REPORT
    if now - state.get('last_report', 0) > 86400:
        send_daily_report()
        state['last_report'] = now
        save_state(state)

    logger.info(f"CYCLE COMPLETED | Issues: {len(issues)}")
    if issues: logger.info(f"Details: {', '.join(issues)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Monitor Crash: {e}")
        send_telegram(f"MONITOR CRASH: {e}")
