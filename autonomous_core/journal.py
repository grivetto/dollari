#!/usr/bin/env python3
import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict

class TradeJournal:
    def __init__(self, log_dir="/home/sergio/denaro"):
        self.log_dir = log_dir
        self.performance_data = defaultdict(lambda: {
            "trades": 0,
            "profit": 0.0,
            "last_trade": None,
            "last_heartbeat": None,
            "status": "UNKNOWN",
            "errors": 0
        })

    def parse_logs(self):
        for filename in os.listdir(self.log_dir):
            if not filename.endswith(".log") or filename == "pnl_aggregator.log" or filename == "health_check.log":
                continue
            
            bot_name = filename.replace(".log", "")
            file_path = os.path.join(self.log_dir, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()[-1000:]
                    for line in lines:
                        if "Heartbeat OK" in line:
                            self.performance_data[bot_name]["last_heartbeat"] = self._extract_timestamp(line)
                            self.performance_data[bot_name]["status"] = "ALIVE"
                        
                        profit_match = re.search(r"(Profit|Earned|Gain)[:\s]+([-+]?\d*\.\d+|\d+)", line, re.IGNORECASE)
                        if profit_match:
                            val = float(profit_match.group(2))
                            self.performance_data[bot_name]["profit"] += val
                            self.performance_data[bot_name]["trades"] += 1
                            self.performance_data[bot_name]["last_trade"] = self._extract_timestamp(line)
                        
                        if any(word in line.upper() for word in ["ERROR", "CRITICAL", "EXCEPTION", "FAILED"]):
                            self.performance_data[bot_name]["errors"] += 1
                            self.performance_data[bot_name]["status"] = "UNHEALTHY"
                            
            except Exception as e:
                print(f"[Journal] Errore lettura {filename}: {e}")

        return self.performance_data

    def _extract_timestamp(self, line):
        match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if match:
            return match.group(1)
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_zombies(self, inactive_hours=24):
        zombies = []
        now = datetime.now()
        for bot, data in self.performance_data.items():
            if data["last_trade"] is None:
                zombies.append(bot)
                continue
            last_trade_dt = datetime.strptime(data["last_trade"], "%Y-%m-%d %H:%M:%S")
            if (now - last_trade_dt).total_seconds() > (inactive_hours * 3600):
                zombies.append(bot)
        return zombies

    def save_report(self, path="/home/sergio/denaro/autonomous_core/performance_report.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.performance_data, f, indent=2)
