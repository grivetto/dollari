import re
with open("mexc_nano_squad.py", "r") as f:
    code = f.read()

code = code.replace("LIVE_TRADING = False", "LIVE_TRADING = True")
code = code.replace("qty = TRADE_AMOUNT_USDT / price", """qty_raw = TRADE_AMOUNT_USDT / price
                            try:
                                mexc.load_markets()
                                qty = float(mexc.amount_to_precision(symbol, qty_raw))
                            except:
                                qty = round(qty_raw, 4)
                            """)

# Same for sell order: we want to sell the exact quantity we bought
# It's already using `qty` which we saved.

with open("mexc_nano_squad.py", "w") as f:
    f.write(code)
print("Patched for LIVE")
