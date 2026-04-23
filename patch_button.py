with open("/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py", "r") as f:
    content = f.read()

# Replace the incorrect load in get_dynamic_kb()
content = content.replace(
    'with open("/home/sergio/.openclaw/workspace/denaro/daily_mission.json", "r") as f:\n                profit_today = float(json.load(f).get("profit_today", 0))',
    'profit_today = float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/total_usdt_cache.json")).get("total_usdt", 0)) - float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/midnight_balance.json")).get("balance", 0))'
)

# And also replace it in get_daily_profit() just in case it was missed
content = content.replace(
    'with open("/home/sergio/.openclaw/workspace/denaro/daily_mission.json", "r") as f:\n                mission_data = __import__("json").load(f)\n                profit_today = float(mission_data.get("profit_today", 0))',
    'profit_today = float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/total_usdt_cache.json")).get("total_usdt", 0)) - float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/midnight_balance.json")).get("balance", 0))\n            with open("/home/sergio/.openclaw/workspace/denaro/daily_mission.json", "r") as f:\n                mission_data = __import__("json").load(f)'
)

with open("/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py", "w") as f:
    f.write(content)
