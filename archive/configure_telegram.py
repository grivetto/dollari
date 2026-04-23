import requests

SERGIO_ID = "277954993"
STELLA_TOKEN = "os.getenv("TELEGRAM_TOKEN")"
TRADING_TOKEN = "os.getenv("TELEGRAM_TOKEN")"

# 1. Rimuovi eventuale tastiera a riquadri da questa chat (Stella) e manda un messaggio
url_msg = f"https://api.telegram.org/bot{STELLA_TOKEN}/sendMessage"
requests.post(url_msg, json={
    "chat_id": SERGIO_ID,
    "text": "🧹 Pulizia dell'interfaccia completata! Ho rimosso i vecchi quadrotti da questa chat.",
    "reply_markup": {"remove_keyboard": True}
})

# 2. Imposta i comandi (Menu Button) per questa chat (Stella)
url_cmds_stella = f"https://api.telegram.org/bot{STELLA_TOKEN}/setMyCommands"
stella_commands = [
    {"command": "status", "description": "Visualizza stato, costi e token"},
    {"command": "memory", "description": "Interroga la mia memoria a lungo termine"},
    {"command": "ping", "description": "Testa la mia latenza e connessione"},
    {"command": "history", "description": "Guarda gli ultimi log della MEXC Nano Squad"}
]
requests.post(url_cmds_stella, json={"commands": stella_commands})

# 3. Imposta i comandi per il Trading Bot (Money Machine)
url_cmds_trading = f"https://api.telegram.org/bot{TRADING_TOKEN}/setMyCommands"
trading_commands = [
    {"command": "start", "description": "Avvia il bot e mostra la plancia principale"}
]
requests.post(url_cmds_trading, json={"commands": trading_commands})

print("Configurazione API completata!")
