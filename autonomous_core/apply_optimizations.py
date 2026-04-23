#!/usr/bin/env python3
# AUTONOMOUS CORE - APPLY OPTIMIZATIONS
# Applica automaticamente le correzioni suggerite per sbloccare i profitti.

import os
import json

class OptimizationApplier:
    def __init__(self, core_dir="/home/sergio/denaro/autonomous_core", bot_dir="/home/sergio/denaro"):
        self.core_dir = core_dir
        self.bot_dir = bot_dir
        self.suggestions_path = os.path.join(core_dir, "optimization_suggestions.json")

    def load_suggestions(self):
        try:
            with open(self.suggestions_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Applier] Errore caricamento suggerimenti: {e}")
            return None

    def patch_file(self, file_path, old_val, new_val):
        """Sostituisce un valore nel file .py"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_val in content:
                new_content = content.replace(old_val, new_val)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        except Exception as e:
            print(f"[Applier] Errore patch {file_path}: {e}")
        return False

    def run(self):
        suggestions = self.load_suggestions()
        if not suggestions:
            return

        applied_count = 0
        for bot, info in suggestions.items():
            if info["category"] == "TOO_CONSERVATIVE":
                for rec in info["recommendations"]:
                    file_path = rec.get("file")
                    if not file_path: continue
                    
                    full_path = os.path.join(self.bot_dir, file_path)
                    
                    # Strategia di rilassamento parametri
                    if rec["parameter"] == "ENTRY_DROP" and rec["current_value"] == "-0.035":
                        if self.patch_file(full_path, "-0.035", "-0.02"):
                            print(f"🚀 {bot}: Entry Drop -0.035 -> -0.02")
                            applied_count += 1
                    
                    elif rec["parameter"] == "TAKE_PROFIT" and rec["current_value"] == "0.02":
                        if self.patch_file(full_path, "0.02", "0.01"):
                            print(f"🚀 {bot}: TP 0.02 -> 0.01")
                            applied_count += 1
                            
                    elif rec["parameter"] == "STOP_LOSS" and rec["current_value"] == "-0.04":
                        if self.patch_file(full_path, "-0.04", "-0.06"):
                            print(f"🚀 {bot}: SL -0.04 -> -0.06")
                            applied_count += 1

        print(f"\n✅ Applicate {applied_count} ottimizzazioni. I bot sono ora più aggressivi.")

if __name__ == "__main__":
    applier = OptimizationApplier()
    applier.run()
