import gc
import gc
with open("telegram_bot_interactive.py", "r") as f:
    code = f.read()

code = code.replace("except Exception as e:\n            gc.collect()\n            time.sleep(5)",
                    "except Exception as e:\n            logging.error(f'ERRORE MAIN LOOP: {e}')\n            gc.collect()\n            time.sleep(5)")

with open("telegram_bot_interactive.py", "w") as f:
    f.write(code)
