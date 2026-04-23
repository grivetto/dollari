#!/usr/bin/env python3
"""
CENTRALIZED PnL AGGREGATOR
Sincronizza e aggrega i PnL da tutte le 3 macchine (MC2, Nuvola, MARCODG1)
Crea un unico source of truth per il portfolio totale.
"""

import json
import os
import time
import logging
from datetime import datetime
from collections import defaultdict
import subprocess
from dotenv import load_dotenv
from binance.client import Client
from logging.handlers import RotatingFileHandler

# CONFIG
CONFIG = {
    "MC2": {
        "ip": "93.43.252.114",
        "user": "sergio",
        "path": "/home/sergio/denaro"
    },
    "NUVOLA": {
        "ip": "87.106.3.15",
        "user": "sergio",
        "path": "/home/sergio/denaro"
    },
    "MARCODG1": {
        "ip": "87.106.222.123",
        "user": "marco",
        "path": "/home/marco/denaro"
    },
    "AGGREGATOR_LOG": "/home/sergio/denaro/pnl_aggregator.log",
    "AGGREGATOR_OUTPUT": "/home/sergio/denaro/portfolio_pnl_realtime.json",
}

# LOGGING
logger = logging.getLogger("PnLAggregator")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(CONFIG["AGGREGATOR_LOG"], maxBytes=5*1024*1024, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

load_dotenv('/home/sergio/denaro/.env')
LOCAL_CLIENT = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))

def get_local_balance():
    """Get balance from MC2 (local)"""
    try:
        account = LOCAL_CLIENT.get_account()
        balances = {}
        for asset in account['balances']:
            total = float(asset['free']) + float(asset['locked'])
            if total > 0:
                balances[asset['asset']] = {
                    "free": float(asset['free']),
                    "locked": float(asset['locked']),
                    "total": total
                }
        return {"MC2": balances, "status": "OK"}
    except Exception as e:
        logger.error(f"MC2 balance error: {e}")
        return {"MC2": {}, "status": "ERROR", "error": str(e)}

def get_remote_mission(machine, ip, user, path):
    """Leggi daily_mission.json da macchina remota"""
    try:
        cmd = f"ssh -o ConnectTimeout=5 {user}@{ip} 'cat {path}/daily_mission.json 2>/dev/null'"
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10, text=True)
        if result.returncode == 0:
            mission = json.loads(result.stdout)
            return mission
    except Exception as e:
        logger.error(f"Remote mission {machine}: {e}")
    return None

def aggregate_pnl():
    """Aggrega PnL da tutte le macchine"""
    logger.info("🔄 Aggregating PnL from all machines...")
    
    portfolio = {
        "timestamp": datetime.now().isoformat(),
        "machines": {},
        "totals": {
            "total_capital_eur": 0,
            "total_daily_profit_eur": 0,
            "total_daily_target_eur": 0,
            "achievement_percent": 0
        }
    }
    
    # MC2 (LOCAL)
    mc2_data = get_local_balance()
    portfolio["machines"]["MC2"] = mc2_data
    
    # NUVOLA
    nuvola_mission = get_remote_mission("NUVOLA", CONFIG["NUVOLA"]["ip"], 
                                        CONFIG["NUVOLA"]["user"], CONFIG["NUVOLA"]["path"])
    portfolio["machines"]["NUVOLA"] = {
        "mission": nuvola_mission,
        "status": "OK" if nuvola_mission else "ERROR"
    }
    
    # MARCODG1
    marcodg1_mission = get_remote_mission("MARCODG1", CONFIG["MARCODG1"]["ip"],
                                          CONFIG["MARCODG1"]["user"], CONFIG["MARCODG1"]["path"])
    portfolio["machines"]["MARCODG1"] = {
        "mission": marcodg1_mission,
        "status": "OK" if marcodg1_mission else "ERROR"
    }
    
    # CALCOLA TOTALI
    total_profit = 0
    total_target = 0
    
    if nuvola_mission:
        total_profit += nuvola_mission.get("profit_today", 0)
        total_target += nuvola_mission.get("target_eur", 0)
    
    if marcodg1_mission:
        total_profit += marcodg1_mission.get("profit_today", 0)
        total_target += marcodg1_mission.get("target_eur", 0)
    
    # Aggiungi MC2 (dalla missione locale)
    try:
        with open('/home/sergio/denaro/daily_mission.json') as f:
            mc2_mission = json.load(f)
            total_profit += mc2_mission.get("profit_today", 0)
            total_target += mc2_mission.get("target_eur", 0)
    except:
        pass
    
    portfolio["totals"]["total_daily_profit_eur"] = total_profit
    portfolio["totals"]["total_daily_target_eur"] = total_target
    if total_target > 0:
        portfolio["totals"]["achievement_percent"] = (total_profit / total_target) * 100
    
    # Salva output
    try:
        with open(CONFIG["AGGREGATOR_OUTPUT"], 'w') as f:
            json.dump(portfolio, f, indent=2)
        logger.info(f"✅ Portfolio saved. Profit: {total_profit:.2f}€ / Target: {total_target:.2f}€ ({portfolio['totals']['achievement_percent']:.1f}%)")
    except Exception as e:
        logger.error(f"Error saving portfolio: {e}")
    
    return portfolio

def main():
    logger.info("🎯 PnL AGGREGATOR STARTED")
    
    while True:
        try:
            portfolio = aggregate_pnl()
            time.sleep(300)  # Aggiorna ogni 5 minuti
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
