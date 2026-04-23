with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

history_block = """
                        elif text == "/HISTORY" or "HISTORY" in text:
                            try:
                                import subprocess
                                log_file = "/home/sergio/.openclaw/workspace/denaro/MEXC_NANO.log"
                                last_logs = subprocess.check_output(["tail", "-n", "20", log_file]).decode()
                                resp_text = f"📜 *STORICO RECENTE (MEXC NANO SQUAD)*\\n`{last_logs[-3500:]}`"
                            except Exception as e:
                                resp_text = "Nessuno storico disponibile o errore di lettura."
"""

code = code.replace('elif text == "/PING" or "PING" in text:', history_block + '\n                        elif text == "/PING" or "PING" in text:')

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)
print("History command added.")
