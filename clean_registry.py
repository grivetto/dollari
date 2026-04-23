import json

CORE_BOTS = {
    # GUARDIANS & INFRASTRUCTURE
    "TG-BOT": "telegram_bot_interactive.py",
    "DASHBOARD": "dashboard_cyberpunk.py",
    "AUTO_HEALER": "auto_healer.py",
    "ROGUE_KILLER": "rogue_killer.py",
    "TARGET_ENFORCER": "target_enforcer.py",
    "AI_RISK_ENGINE": "ai_risk_engine.py",
    "BOT_STATUS_CACHE": "update_bot_status.py",
    "CACHE_UPD": "update_cache.py",
    
    # NUVOLA SPOT LEGIONS
    "SNIPER_SQUAD": "sniper_squad.py",
    "DCA_ACCUMULATOR": "dca_accumulator.py",
    "VAMPIRE_GRID": "vampire_grid.py",
    "GARIBAN": "gariban_beggar.py",
    
    # INTELLIGENCE
    "MEV_BRAIN": "mev_sandwich_bot.py",
    "FUNDING_ARB": "funding_arbitrage_estremo.py",
    "ALPHA_STRIKE": "alpha_strike_scalper.py",
    "ASIAN_ECHO": "asian_echo_sniper.py"
}

with open('/home/sergio/.openclaw/workspace/denaro/lite_guardian.py', 'r') as f:
    lines = f.readlines()

with open('/home/sergio/.openclaw/workspace/denaro/lite_guardian.py', 'w') as f:
    in_registry = False
    for line in lines:
        if line.startswith("BOT_REGISTRY = {"):
            in_registry = True
            f.write("BOT_REGISTRY = {\n")
            for k, v in CORE_BOTS.items():
                f.write(f'    "{k}": "{v}",\n')
            f.write("}\n")
        elif in_registry and line.strip() == "}":
            in_registry = False
        elif not in_registry:
            f.write(line)
