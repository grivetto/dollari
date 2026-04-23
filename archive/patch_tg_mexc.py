import re

with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

mexc_logic = """
def get_mexc_status():
    try:
        import ccxt
        import os
        from dotenv import load_dotenv
        load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.mexc')
        api_key = os.getenv('MEXC_API_KEY')
        if not api_key: return "⚠️ API MEXC non configurate."
        
        mexc = ccxt.mexc({'apiKey': api_key, 'secret': os.getenv('MEXC_API_SECRET'), 'options': {'defaultType': 'spot'}})
        bal = mexc.fetch_balance()
        free_usdt = float(bal.get('USDT', {}).get('free', 0.0))
        total_usdt = float(bal.get('USDT', {}).get('total', 0.0))
        
        log_file = "/home/sergio/.openclaw/workspace/denaro/MEXC_NANO.log"
        last_logs = ""
        try:
            import subprocess
            last_logs = subprocess.check_output(["tail", "-n", "3", log_file]).decode()
        except: pass
        
        msg = f"🧪 *LABORATORIO MEXC (0% FEE)*\\n"
        msg += f"------------------------------------\\n"
        msg += f"💰 *Capitale Libero:* {free_usdt:.2f} USDT\\n"
        msg += f"🏦 *Capitale Totale:* {total_usdt:.2f} USDT\\n"
        msg += f"------------------------------------\\n"
        msg += f"📜 *Ultimi 3 Log Operativi:*\\n`{last_logs}`"
        return msg
    except Exception as e:
        return f"⚠️ Errore lettura MEXC: {str(e)}"
"""

# Insert the get_mexc_status function before main_loop
code = code.replace("def main_loop():", mexc_logic + "\ndef main_loop():")

# Update get_dynamic_kb to include the new button
old_keyboard = """
        return {
            "keyboard": [
                [{"text": btn_text}, {"text": "Ricavo Giornaliero"}],
                [{"text": "Andamento Ricavi"}, {"text": "Stato Squadre"}],
                [{"text": "Dashboard Web"}, {"text": "Elemosina Gariban"}]
            ],
            "resize_keyboard": True
        }
"""
# Note: the old_keyboard formatting might vary slightly. Let's use regex.
import re

kb_replacement = r"""return {
        "keyboard": [
            [{"text": btn_text}, {"text": "Ricavo Giornaliero"}],
            [{"text": "MEXC Laboratorio"}, {"text": "Stato Squadre"}],
            [{"text": "Dashboard Web"}, {"text": "Andamento Ricavi"}]
        ],
        "resize_keyboard": True
    }"""
code = re.sub(r'return\s*\{\s*"keyboard":\s*\[(.*?)\]\,\s*"resize_keyboard":\s*True\s*\}', kb_replacement, code, flags=re.DOTALL)

# Add the 'elif' condition
mexc_elif = """
                        elif "MEXC" in text:
                            resp_text = get_mexc_status()
"""
code = code.replace('elif "CIFRA" in text:', mexc_elif + '\n                        elif "CIFRA" in text:')

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)

print("Patch Telegram MEXC applicata")
