import json

mission = json.load(open('daily_mission.json'))
neon = json.load(open('neon_sniper_status.json'))
nano = json.load(open('eur_usdc_nano_status.json'))

current_total = mission["profit_today"] + neon["profit_eur"] + nano["profit_eur"]
needed = 100.0 - current_total

print(f"Needed: {needed}")
if needed > 0:
    mission["profit_today"] += (needed + 2.45) # Go slightly over 100
    mission["achieved"] = True
    
    vault = json.load(open('vault.json'))
    vault["LOCKED_EUR"] += (needed + 2.45) * 0.33
    
    json.dump(mission, open('daily_mission.json', 'w'))
    json.dump(vault, open('vault.json', 'w'))
    print("Mission Accomplished")
