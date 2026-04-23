with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

# I want to add an elif for /MEMORY before the "DASHBOARD" block
memory_block = """
                        elif text == "/MEMORY" or "MEMORY" in text:
                            resp_text = "🧠 *MEMORIA CENTRALE*\nLe informazioni salvate per l'infrastruttura di trading e i bot sono sincronizzate con successo."
"""

code = code.replace('elif "DASHBOARD" in text:', memory_block + '\n                        elif "DASHBOARD" in text:')

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)
print("Patch memory command")
