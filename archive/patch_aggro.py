with open("mexc_nano_squad.py", "r") as f:
    code = f.read()

code = code.replace("TAKE_PROFIT_PCT = 1.004  # +0.4% profit target", "TAKE_PROFIT_PCT = 1.0015  # +0.15% (High Freq)")
code = code.replace("RSI_BUY_THRESHOLD = 38   # Ingresso aggressivo", "RSI_BUY_THRESHOLD = 45   # Molto più aggressivo")

with open("mexc_nano_squad.py", "w") as f:
    f.write(code)
print("Aggro patch applicata")
