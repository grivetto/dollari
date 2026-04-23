with open("telegram_bot_interactive.py", "r") as f: code = f.read()
code = code.replace("if chat_id != sergio_id: logging.info(f\\\"UNAUTHORIZED USER: {chat_id}\\\"); continue",
                    "if chat_id != sergio_id: logging.info(f\\\"UNAUTHORIZED USER: {chat_id}\\\"); continue\\n                        logging.info(f\\\"RICEVUTO MESSAGGIO: {text}\\\")")
with open("telegram_bot_interactive.py", "w") as f: f.write(code)
print("Patch applied")
