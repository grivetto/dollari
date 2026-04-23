#!/usr/bin/env python3
# AUTONOMOUS CORE - OPTIMIZER (v4)
# Analizza le performance e suggerisce ottimizzazioni includendo i "Magic Numbers" della Legion

import os
import json
import re

class StrategyOptimizer:
    def __init__(self, core_dir="/home/sergio/denaro/autonomous_core", bot_dir="/home/sergio/denaro"):
        self.core_dir = core_dir
        self.bot_dir = bot_dir
        self.report_path = os.path.join(core_dir, "performance_report.json")
        self.suggestions_path = os.path.join(core_dir, "optimization_suggestions.json")

    def load_performance(self):
        try:
            with open(self.report_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Optimizer] Errore caricamento report: {e}")
            return None

    def find_bot_file(self, bot_name):
        exact = os.path.join(self.bot_dir, f"{bot_name}.py")
        if os.path.exists(exact):
            return exact
        
        keyword = bot_name.split('_')[-1].lower() if '_' in bot_name else bot_name.lower()
        try:
            for filename in os.listdir(self.bot_dir):
                if filename.endswith(".py") and keyword in filename.lower():
                    return os.path.join(self.bot_dir, filename)
        except Exception as e:
            print(f"[Optimizer] Errore durante ls {self.bot_dir}: {e}")
        return None

    def analyze_bot_code(self, bot_name):
        file_path = self.find_bot_file(bot_name)
        if not file_path:
            return [{"parameter": "FILE", "current_value": "NOT_FOUND", "advice": "File di codice non trovato"}]

        suggestions = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Definizione pattern: (Regex, Advice)
                patterns = {
                    "RSI_LOW": (r"RSI_LOW\s*=\s*(\d+)", "Aumenta per essere meno conservativo"),
                    "RSI_HIGH": (r"RSI_HIGH\s*=\s*(\d+)", "Diminuisci per essere meno conservativo"),
                    "MIN_PROFIT": (r"MIN_PROFIT\s*=\s*([\d.]+)", "Diminuisci per chiudere trade più velocemente"),
                    "TAKE_PROFIT": (r"pnl\s*>=?\s*([\d.]+)", "Diminuisci il TP per aumentare la frequenza di chiusura"),
                    "STOP_LOSS": (r"pnl\s*<=?\s*([\d.-]+)", "Allarga lo SL per evitare stop prematuri"),
                    "ENTRY_DROP": (r"drop\s*<=?\s*([\d.-]+)", "Aumenta la soglia (es. da -0.035 a -0.02) per entrare più spesso"),
                    "GRID_SIZE": (r"GRID_SIZE\s*=\s*(\d+)", "Riduci la dimensione"),
                }

                for param, (regex, advice) in patterns.items():
                    match = re.search(regex, content)
                    if match:
                        current_val = match.group(1)
                        suggestions.append({
                            "parameter": param,
                            "current_value": current_val,
                            "advice": advice,
                            "file": os.path.basename(file_path)
                        })
        except Exception as e:
            print(f"[Optimizer] Errore analisi {bot_name}: {e}")
        
        return suggestions

    def run_optimization(self):
        data = self.load_performance()
        if not data: return
        
        all_suggestions = {}
        for bot, info in data.items():
            if info["status"] == "ALIVE" and info["trades"] == 0:
                suggestions = self.analyze_bot_code(bot)
                if suggestions:
                    all_suggestions[bot] = {
                        "category": "TOO_CONSERVATIVE",
                        "reason": "Bot attivo ma non tradano. Parametri troppo restrittivi.",
                        "recommendations": suggestions
                    }
            elif info["profit"] < 0:
                suggestions = self.analyze_bot_code(bot)
                if suggestions:
                    all_suggestions[bot] = {
                        "category": "UNPROFITABLE",
                        "reason": f"Profitto negativo: {info['profit']}.",
                        "recommendations": suggestions
                    }

        with open(self.suggestions_path, "w") as f:
            json.dump(all_suggestions, f, indent=2)
        return all_suggestions

if __name__ == "__main__":
    optimizer = StrategyOptimizer()
    results = optimizer.run_optimization()
    if results:
        print(f"✅ Ottimizzazione completata. {len(results)} bot analizzati.")
    else:
        print("ℹ️ Nessun suggerimento trovato.")
