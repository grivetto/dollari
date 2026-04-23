import os, glob

ALLOWED_LOGS = [
    "TG-BOT.log", "DASHBOARD.log", "AUTO_HEALER.log", "ROGUE_KILLER.log", "TARGET_ENFORCER.log", "AI_RISK.log", "AI_RISK_ENGINE.log", "BOT_STATUS_CACHE.log", "CACHE_UPD.log", "SNIPER_SQUAD.log", "DCA_ACCUMULATOR.log", "VAMPIRE_GRID.log", "GARIBAN.log", "MEV_BRAIN.log", "FUNDING_ARB.log", "ALPHA_STRIKE.log", "ASIAN_ECHO.log", "ORBITAL_WS.log", "MIDNIGHT_SWEEPER.log"
]

all_logs = glob.glob("/home/sergio/.openclaw/workspace/denaro/*.log")
for log in all_logs:
    base = os.path.basename(log)
    if base not in ALLOWED_LOGS:
        print(f"DELETING {base}")
        os.remove(log)

