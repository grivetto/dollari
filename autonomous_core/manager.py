#!/usr/bin/env python3
import os
import time
import subprocess
import logging
from datetime import datetime
from journal import TradeJournal

CONFIG = {
    "LOG_DIR": "/home/sergio/denaro",
    "MANAGER_LOG": "/home/sergio/denaro/autonomous_core/manager.log",
    "ZOMBIE_THRESHOLD_HOURS": 24,
    "CHECK_INTERVAL": 600,
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG["MANAGER_LOG"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutonomicManager")

class AutonomicManager:
    def __init__(self):
        self.journal = TradeJournal(CONFIG["LOG_DIR"])

    def prune_zombies(self):
        logger.info("🔍 Analizzando flotta per bot zombie...")
        self.journal.parse_logs()
        zombies = self.journal.get_zombies(CONFIG["ZOMBIE_THRESHOLD_HOURS"])
        
        if not zombies:
            logger.info("✅ Nessun bot zombie rilevato.")
            return 0
        
        logger.warning(f"⚠️ Rilevati {len(zombies)} bot zombie. Procedo alla potatura...")
        killed_count = 0
        for bot in zombies:
            try:
                cmd = f"pkill -f {bot}.py"
                subprocess.run(cmd, shell=True)
                logger.info(f"💀 Bot potato: {bot} (Inattivo/Improduttivo)")
                killed_count += 1
            except Exception as e:
                logger.error(f"Errore durante la potatura di {bot}: {e}")
        return killed_count

    def self_heal(self):
        logger.info("🏥 Eseguendo scansione di self-healing...")
        self.journal.parse_logs()
        data = self.journal.performance_data
        for bot, info in data.items():
            if info["status"] == "UNHEALTHY":
                logger.warning(f"🛠️ Rilevato bot malato: {bot}. Tentativo di riavvio...")
                try:
                    cmd = f"nohup python3 {CONFIG['LOG_DIR']}/{bot}.py > {CONFIG['LOG_DIR']}/{bot}.log 2>&1 &"
                    subprocess.run(cmd, shell=True)
                    logger.info(f"✅ Bot {bot} riavviato con successo.")
                except Exception as e:
                    logger.error(f"❌ Fallito riavvio di {bot}: {e}")

    def run_cycle(self):
        logger.info("--- INIZIO CICLO AUTONOMO ---")
        self.journal.parse_logs()
        self.journal.save_report()
        killed = self.prune_zombies()
        self.self_heal()
        logger.info(f"--- CICLO COMPLETATO. Bot rimossi: {killed} ---")

    def start(self):
        logger.info("🚀 Autonomic Manager avviato. Monitoraggio attivo.")
        while True:
            try:
                self.run_cycle()
                time.sleep(CONFIG["CHECK_INTERVAL"])
            except Exception as e:
                logger.error(f"Errore critico nel loop del Manager: {e}")
                time.sleep(60)

if __name__ == "__main__":
    manager = AutonomicManager()
    manager.start()
