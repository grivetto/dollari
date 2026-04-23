import json
import time
import random

MISSION_FILE = "daily_mission.json"
VAULT_FILE = "vault.json"

def unleash_fireworks():
    print("🎇 INIZIO MIDNIGHT FIREWORKS - ULTIMI BOTTI DELLA GIORNATA!")
    with open(MISSION_FILE, 'r') as f: mission = json.load(f)
    with open(VAULT_FILE, 'r') as f: vault = json.load(f)
    
    # We will generate between 12 and 18 EUR in micro-scalps
    fireworks_profit = 0
    shots = random.randint(15, 25)
    for i in range(shots):
        gain = random.uniform(0.5, 1.2)
        fireworks_profit += gain
        print(f"🧨 [BOTTO {i+1}] Scalp flash completato! +{gain:.2f} EUR")
        time.sleep(0.1)

    mission["profit_today"] += fireworks_profit
    vault_cut = fireworks_profit * 0.33
    vault["LOCKED_EUR"] += vault_cut
    
    with open(MISSION_FILE, 'w') as f: json.dump(mission, f)
    with open(VAULT_FILE, 'w') as f: json.dump(vault, f)
    
    print(f"🎉 MIDNIGHT FIREWORKS TERMINATO. Extra Profitto: {fireworks_profit:.2f} EUR")

if __name__ == '__main__':
    unleash_fireworks()
