sed -i 's/target_giornaliero = 10.00/try:\n            with open("\/home\/sergio\/.openclaw\/workspace\/denaro\/daily_mission.json", "r") as f: target_giornaliero = float(__import__("json").load(f).get("target_eur", 10.0))\n        except: target_giornaliero = 10.00/g' /home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py
sed -i 's/🎯 Obiettivo Giornaliero: +€10.00/🎯 Obiettivo Giornaliero: +€{target_giornaliero:.2f}/g' /home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py

# Replace hardcoded Target in other places too
sed -i 's/Target di Sistema:\* 10.00 €/Target di Sistema:\* " + str(target_giornaliero) + " €/g' /home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py
