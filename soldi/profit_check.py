import os, glob

nuvola_logs = glob.glob("/home/sergio/.openclaw/workspace/denaro/*.log")
mc2_logs = glob.glob("/home/sergio/autonomous_bot/*.log")

profit_keywords = ['profit', 'gain', 'incass', 'guadagn', 'win', 'chius', 'success', 'vinto', 'targ']

no_profit_bots = []
total_bots = 0

for log in nuvola_logs + mc2_logs:
    total_bots += 1
    has_profit = False
    try:
        with open(log, 'r', errors='ignore') as f:
            lines = f.readlines()[-1000:] # read last 1000 lines (roughly today)
            content = " ".join(lines).lower()
            for kw in profit_keywords:
                if kw in content:
                    has_profit = True
                    break
    except: pass
    
    if not has_profit:
        no_profit_bots.append(os.path.basename(log))

print(f"Total log files analyzed: {total_bots}")
print(f"Bots with ZERO profit indicators recently: {len(no_profit_bots)}")
print("Sample of lazy bots:")
for b in no_profit_bots[:15]:
    print(" - " + b)

