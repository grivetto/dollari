import re
with open("lite_guardian.py", "r") as f:
    content = f.read()

# Add import
if "import roc_momentum_sniper" not in content:
    content = "import roc_momentum_sniper\n" + content

# Add call inside run_strategies()
if "roc_momentum_sniper.check_roc_momentum()" not in content:
    target = "    donchian_channel_breakout.check_donchian_channel_breakout()\n"
    replacement = "    donchian_channel_breakout.check_donchian_channel_breakout()\n    roc_momentum_sniper.check_roc_momentum()\n"
    content = content.replace(target, replacement)

with open("lite_guardian.py", "w") as f:
    f.write(content)
