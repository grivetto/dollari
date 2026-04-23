#!/usr/bin/env python3
"""
DENARO AUTONOMOUS MONITOR — H24
Gira ogni 5 minuti su NUVOLA
Monitora e auto-ripara:
- Tutti i bot su Nuvola e MC2
- Connessione Binance
- Memoria/CPU risorse
- Log errori critici
"""

import subprocess
import os
import time
import json
import logging
from datetime import datetime

os.makedirs('/home/sergio/.openclaw/workspace/denaro/monitor', exist_ok=True)
LOG_FILE = '/home/sergio/.openclaw/workspace/denaro/monitor/monitor.log'
STATE_FILE = '/home/sergio/.openclaw/workspace/denaro/monitor/state.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [MONITOR] - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE)]
)
logger = logging.getLogger(__name__)

MC2_CMD = 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p 2222 sergio@93.43.252.114'

BOTS_NUVOLA = [
    {'name': 'grid_bot_v2', 'pattern': 'grid_bot_v2', 'py': '/home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/python3', 'script': '/home/sergio/.openclaw/workspace/denaro/grid_bot_v2.py', 'workdir': '/home/sergio/.openclaw/workspace/denaro'},
    {'name': 'telegram_bot', 'pattern': 'telegram_bot_interactive', 'py': '/home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/python3', 'script': '/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py', 'workdir': '/home/sergio/.openclaw/workspace/denaro'},
    {'name': 'hermes_chat', 'pattern': 'hermes_chat_bot', 'py': '/home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/python3', 'script': '/home/sergio/.openclaw/workspace/denaro/hermes_chat_bot.py', 'workdir': '/home/sergio/.openclaw/workspace/denaro'},
    {'name': 'dashboard_v3', 'pattern': 'dashboard_v3_unified', 'py': '/home/sergio/.openclaw/workspace/denaro/trading_bot_env/bin/python3', 'script': '/home/sergio/.openclaw/workspace/denaro/dashboard_v3_unified.py', 'workdir': '/home/sergio/.openclaw/workspace/denaro'},
]

BOTS_MC2 = [
    {'name': 'sniper_v2', 'pattern': 'rebound_sniper_v2', 'py': '/home/sergio/denaro/venv/bin/python3', 'script': '/home/sergio/denaro/rebound_sniper_v2.py', 'workdir': '/home/sergio/denaro'},
    {'name': 'trend_follow', 'pattern': 'trend_following_bot', 'py': '/home/sergio/denaro/venv/bin/python3', 'script': '/home/sergio/denaro/trend_following_bot.py', 'workdir': '/home/sergio/denaro'},
    {'name': 'dca_bot', 'pattern': 'dca_bot', 'py': '/home/sergio/denaro/venv/bin/python3', 'script': '/home/sergio/denaro/dca_bot.py', 'workdir': '/home/sergio/denaro'},
    {'name': 'status_server', 'pattern': 'mc2_status_server', 'py': '/home/sergio/denaro/venv/bin/python3', 'script': '/home/sergio/denaro/mc2_status_server.py', 'workdir': '/home/sergio/denaro'},
]


def shell(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', 'TIMEOUT'
    except Exception as e:
        return -1, '', str(e)


def mc2(cmd, timeout=20):
    return shell(MC2_CMD + " " + cmd, timeout)


def is_alive(pattern, on_mc2=False):
    cmd = "ps -ef | grep " + pattern + " | grep -v grep | wc -l"
    if on_mc2:
        rc, out, _ = mc2(cmd)
    else:
        rc, out, _ = shell(cmd)
    try:
        return int(out.strip()) > 0
    except (ValueError, AttributeError):
        return False


def start_bot(bot, on_mc2=False):
    cmd = "setsid " + bot['py'] + " " + bot['script'] + " < /dev/null >> /dev/null 2>&1 &"
    if on_mc2:
        rc, _, err = mc2(cmd, timeout=10)
        prefix = "MC2"
    else:
        rc, _, err = shell(cmd, timeout=10)
        prefix = "Nuvola"
    if rc == 0:
        logger.info("✅ Avviato %s (%s)", bot['name'], prefix)
    else:
        logger.error("❌ Errore avvio %s: %s", bot['name'], err[:200])
    return rc == 0


def check_binance():
    try:
        import ccxt
        from dotenv import load_dotenv
        load_dotenv('/home/sergio/denaro/.env')
        ex = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        ticker = ex.fetch_ticker('ETH/EUR')
        logger.info("✅ Binance OK | ETH/EUR:EUR %.2f", ticker['last'])
        return True
    except Exception as e:
        logger.warning("⚠️ Binance check failed: %s", e)
        return False


def check_resources():
    rc, out, _ = shell("free -m | grep Mem | awk '{printf \"used:%s/%sMB (%d%%)\", $3, $2, $3/$2*100}'")
    if out:
        logger.info("💾 Nuvola RAM: %s", out)

    rc2, out2, _ = mc2("free -m | grep Mem | awk '{printf \"used:%s/%sMB (%d%%)\", $3, $2, $3/$2*100}'")
    if out2:
        logger.info("💾 MC2 RAM: %s", out2)


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {'restarts': {}, 'issues': []}


def save_state(state):
    state['issues'] = state.get('issues', [])[-100:]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def run_monitoring():
    now = datetime.now().isoformat()
    logger.info("=" * 50)
    logger.info("MONITORING CYCLE — %s", now)
    logger.info("=" * 50)

    state = load_state()
    issues_found = 0

    # 1. Binance
    check_binance()

    # 2. Resources
    check_resources()

    # 3. Nuvola bots
    logger.info("--- Nuvola Bots ---")
    for bot in BOTS_NUVOLA:
        key = "nuvola_" + bot['name']
        alive = is_alive(bot['pattern'])
        if not alive:
            logger.warning("❌ %s DOWN on Nuvola — restarting...", bot['name'])
            if start_bot(bot):
                state['restarts'][key] = state['restarts'].get(key, 0) + 1
                issues_found += 1
                state['issues'].append({'time': now, 'bot': key, 'action': 'restarted'})
            else:
                logger.error("❌ FAILED to restart %s", bot['name'])
                state['issues'].append({'time': now, 'bot': key, 'action': 'restart_failed'})
        else:
            logger.info("✅ %s OK", bot['name'])
        time.sleep(2)

    # 4. MC2 bots
    logger.info("--- MC2 Bots ---")
    rc_test, _, _ = mc2('echo OK')
    if rc_test != 0:
        logger.error("❌ MC2 NOT REACHABLE")
        state['issues'].append({'time': now, 'bot': 'mc2_connectivity', 'action': 'unreachable'})
    else:
        logger.info("✅ MC2 reachable")
        for bot in BOTS_MC2:
            key = "mc2_" + bot['name']
            alive = is_alive(bot['pattern'], on_mc2=True)
            if not alive:
                logger.warning("❌ %s DOWN on MC2 — restarting...", bot['name'])
                if start_bot(bot, on_mc2=True):
                    state['restarts'][key] = state['restarts'].get(key, 0) + 1
                    issues_found += 1
                    state['issues'].append({'time': now, 'bot': key, 'action': 'restarted'})
                else:
                    logger.error("❌ FAILED to restart %s", bot['name'])
                    state['issues'].append({'time': now, 'bot': key, 'action': 'restart_failed'})
            else:
                logger.info("✅ %s OK", bot['name'])

    # 5. Nginx MC2
    rc_nginx, _, _ = mc2('systemctl is-active nginx')
    if rc_nginx == 0:
        logger.info("✅ Nginx MC2 OK")
    else:
        logger.warning("⚠️ Nginx not active on MC2")
        mc2('sudo systemctl start nginx')
        issues_found += 1

    # 6. Dashboard Nuvola
    rc_dash, out, _ = shell('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/', timeout=10)
    if out == '200':
        logger.info("✅ Dashboard Nuvola :8081 OK")
    else:
        logger.warning("⚠️ Dashboard Nuvola %s", out)
        # Try to restart
        for bot in BOTS_NUVOLA:
            if bot['name'] == 'dashboard_v3':
                if not is_alive(bot['pattern']):
                    start_bot(bot)

    # 7. Dashboard MC2
    rc_d2, out2, _ = shell('curl -sk -o /dev/null -w "%{http_code}" https://mgrivett.ddns.net/', timeout=15)
    if out2 == '200':
        logger.info("✅ Dashboard MC2 mgrivett.ddns.net OK")
    else:
        logger.warning("⚠️ Dashboard MC2 HTTP %s", out2)
        # Check if status server is running
        if not is_alive('mc2_status_server', on_mc2=True):
            logger.warning("❌ Status server DOWN — restarting")
            for bot in BOTS_MC2:
                if bot['name'] == 'status_server':
                    start_bot(bot, on_mc2=True)
        issues_found += 1

    # Summary
    counts = state.get('restarts', {})
    summary = ' | '.join(k + ':' + str(v) for k, v in counts.items() if v > 0)
    logger.info("=" * 50)
    logger.info("CYCLE COMPLETED | Issues: %d | Total restarts: %s", issues_found, summary)
    logger.info("=" * 50)

    save_state(state)


if __name__ == '__main__':
    run_monitoring()
