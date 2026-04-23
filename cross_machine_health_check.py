#!/usr/bin/env python3
"""
CROSS-MACHINE HEALTH CHECK DAEMON
Monitora tutti e 3 i sistemi ogni 60 secondi e genera alert su problemi.
"""

import os
import time
import json
import subprocess
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from binance.client import Client

CONFIG = {
    "MACHINES": {
        "MC2": {"ip": "93.43.252.114", "user": "sergio"},
        "NUVOLA": {"ip": "87.106.3.15", "user": "sergio"},
        "MARCODG1": {"ip": "87.106.222.123", "user": "marco"}
    },
    "CHECK_INTERVAL": 60,
    "LOG_FILE": "/home/sergio/denaro/health_check.log",
    "ALERT_FILE": "/home/sergio/denaro/health_alerts.json",
}

logger = logging.getLogger("HealthCheck")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(CONFIG["LOG_FILE"], maxBytes=5*1024*1024, backupCount=3)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

def check_machine_health(machine, ip, user):
    """Verifica salute di una singola macchina"""
    try:
        # Prova connessione SSH + carica sistema
        cmd = f"ssh -o ConnectTimeout=5 {user}@{ip} 'uptime && free -h && ps aux | wc -l'"
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10, text=True)
        
        if result.returncode != 0:
            return {"status": "DOWN", "error": "SSH connection failed"}
        
        lines = result.stdout.strip().split('\n')
        uptime_line = lines[0] if lines else "unknown"
        
        # Estrai load average
        if "load average:" in uptime_line:
            load_str = uptime_line.split("load average:")[1].strip()
            load_vals = [float(x.rstrip(',')) for x in load_str.split()[:3]]
            
            status = "OK"
            alerts = []
            
            if load_vals[0] > 3.0:
                status = "WARNING"
                alerts.append(f"High CPU load: {load_vals[0]}")
            
            if "Memory usage:" in uptime_line or len(lines) > 1:
                # Cerca linea memoria
                for line in lines:
                    if "Mem:" in line:
                        alerts.append(f"Memory check: {line}")
            
            return {
                "status": status,
                "load_average": load_vals,
                "uptime": uptime_line,
                "alerts": alerts
            }
    except Exception as e:
        logger.error(f"Health check {machine}: {e}")
        return {"status": "ERROR", "error": str(e)}

def check_bots_running(machine, ip, user, path):
    """Conta bot attivi su macchina"""
    try:
        cmd = f"ssh -o ConnectTimeout=5 {user}@{ip} 'ps aux | grep -E \"python.*\\.py\" | grep -v grep | wc -l'"
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10, text=True)
        
        if result.returncode == 0:
            count = int(result.stdout.strip())
            return {"bots_running": count}
    except Exception as e:
        logger.error(f"Bot count {machine}: {e}")
        return {"bots_running": 0, "error": str(e)}
    
    return {"bots_running": 0}

def health_check_cycle():
    """Esegui ciclo completo di health check"""
    alerts = []
    status_report = {
        "timestamp": datetime.now().isoformat(),
        "machines": {}
    }
    
    for machine, config in CONFIG["MACHINES"].items():
        logger.info(f"🔍 Checking {machine}...")
        
        health = check_machine_health(machine, config["ip"], config["user"])
        bots = check_bots_running(machine, config["ip"], config["user"], "/tmp")
        
        status_report["machines"][machine] = {
            "health": health,
            "bots": bots
        }
        
        if health["status"] in ["DOWN", "ERROR"]:
            alerts.append({
                "machine": machine,
                "severity": "CRITICAL",
                "message": f"{machine} is {health['status']}: {health.get('error', 'unknown')}"
            })
        elif health["status"] == "WARNING":
            for alert in health.get("alerts", []):
                alerts.append({
                    "machine": machine,
                    "severity": "WARNING",
                    "message": alert
                })
        
        if bots.get("bots_running", 0) < 2:
            alerts.append({
                "machine": machine,
                "severity": "WARNING",
                "message": f"Low bot count: {bots.get('bots_running', 0)}"
            })
    
    # Salva report
    try:
        with open(CONFIG["ALERT_FILE"], 'w') as f:
            json.dump({"alerts": alerts, "report": status_report}, f, indent=2)
        
        if alerts:
            logger.warning(f"⚠️  {len(alerts)} alerts detected!")
            for alert in alerts:
                logger.warning(f"  [{alert['severity']}] {alert['machine']}: {alert['message']}")
        else:
            logger.info("✅ All systems healthy")
    
    except Exception as e:
        logger.error(f"Error saving alerts: {e}")

def main():
    logger.info("🏥 HEALTH CHECK DAEMON started")
    
    while True:
        try:
            health_check_cycle()
            time.sleep(CONFIG["CHECK_INTERVAL"])
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
