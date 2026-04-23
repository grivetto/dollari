with open("/home/sergio/.openclaw/workspace/denaro/lite_guardian.py", "r") as f:
    content = f.read()

import re
if "MEXC_NANO" not in content:
    content = content.replace('BOT_REGISTRY["GARIBAN"] = "gariban_beggar.py"', 'BOT_REGISTRY["GARIBAN"] = "gariban_beggar.py"\n    BOT_REGISTRY["MEXC_NANO"] = "mexc_nano_squad.py"\n    BOT_REGISTRY["KAMIKAZE"] = "kamikaze_bitget_futures.py"')
    with open("/home/sergio/.openclaw/workspace/denaro/lite_guardian.py", "w") as f:
        f.write(content)
