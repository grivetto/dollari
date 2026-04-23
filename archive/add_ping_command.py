with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

ping_block = """
                        elif text == "/PING" or "PING" in text:
                            resp_text = "🏓 *PONG!*\nTutti i sistemi operativi. Tempi di risposta ottimali."
"""

code = code.replace('elif text == "/MEMORY" or "MEMORY" in text:', ping_block + '\n                        elif text == "/MEMORY" or "MEMORY" in text:')

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)
print("Patch ping command")
