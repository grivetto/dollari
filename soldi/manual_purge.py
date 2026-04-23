import os, time

ALLOWED = [
    "lite_guardian.py", "heavy_guardian.py", "rogue_killer.py", "auto_healer.py", "update_bot_status.py", "update_cache.py", "telegram_bot_interactive.py", "generate_monitoring.py", "midnight_sweeper.py", "hourly_reporter.py", "ai_risk_engine.py", "mev_sandwich_bot.py", "auto_healer_mc2.py", "auto_healer_mc3.py", "dashboard_cyberpunk.py", "target_enforcer.py", "sniper_squad.py", "dca_accumulator.py", "vampire_grid.py", "gariban_beggar.py", "funding_arbitrage_estremo.py", "alpha_strike_scalper.py", "asian_echo_sniper.py", "orbital_websocket.py"
]

ps_output = os.popen("ps aux | grep python").read().split('\n')
for line in ps_output:
    if "workspace/denaro/" in line and "grep" not in line and "manual_purge" not in line:
        parts = line.split()
        pid = parts[1]
        script_name = None
        for part in parts:
            if ".py" in part and "denaro" in part:
                script_name = part.split('/')[-1]
                break
        
        if script_name and script_name not in ALLOWED:
            print(f"KILLING {script_name} PID {pid}")
            os.system(f"kill -9 {pid}")
