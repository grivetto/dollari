import re

with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

new_kb = """        return {
        "keyboard": [
            [{"text": btn_text}, {"text": "Dashboard Web"}],
            [{"text": "MEXC Laboratorio"}, {"text": "Stato Squadre"}],
            [{"text": "Andamento Ricavi"}, {"text": "Elemosina Gariban"}]
        ],
        "resize_keyboard": True
    }"""

# Trova "return {" ... "resize_keyboard": True }"
code = re.sub(r'return \{\s*"keyboard": \[.*?\]\,\s*"resize_keyboard": True\s*\}', new_kb, code, flags=re.DOTALL)

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)

print("Grid FORZATA.")
