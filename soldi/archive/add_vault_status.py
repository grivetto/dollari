import re

with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

new_logic = """        profit = total_eur - CAPITALE_VERSATO_TOTALE
        
        locked = 0.0
        gariban = 0.0
        try:
            with open("/home/sergio/.openclaw/workspace/denaro/vault.json", "r") as vf:
                vdata = __import__("json").load(vf)
                locked = float(vdata.get("LOCKED_EUR", 0))
                gariban = float(vdata.get("GARIBAN_TRACKER", 0))
        except: pass
        
        main_vault = locked - gariban
        
        msg = (
            f"💰 *SITUAZIONE CAPITALE*\n"
            f"------------------------------------\n"
            f"🏦 Valore Attuale: €{total_eur:.2f}\n"
            f"📥 Cifra Investita: €{CAPITALE_VERSATO_TOTALE:.2f}\n"
            f"📈 Profitto Totale: {profit:+.2f} €\n"
            f"------------------------------------\n"
            f"🔐 Cassaforte (33%): €{main_vault:.2f}\n"
            f"🤲 Elemosina Gariban: €{gariban:.2f}\n"
            f"🛡️ **TOTALE PROTETTO**: €{locked:.2f}\n"
            f"------------------------------------"
        )
        return msg"""

code = re.sub(r'profit = total_eur - CAPITALE_VERSATO_TOTALE.*?return msg', new_logic, code, flags=re.DOTALL)

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)

print("Status patched.")
