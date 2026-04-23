with open("/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py", "r") as f:
    content = f.read()

content = content.replace(
    'resp_text = f"📥 *CIFRA INVESTITA ALL\'INIZIO*\\n------------------------------------\\nTotale versato storicamente: *€{CAPITALE_VERSATO_TOTALE:.2f}*\\n(Questo è il tuo capitale di partenza usato come riferimento per i profitti globali)."',
    'try:\n                                pt = float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/total_usdt_cache.json")).get("total_usdt", 0)) - float(__import__("json").load(open("/home/sergio/.openclaw/workspace/denaro/midnight_balance.json")).get("balance", 0))\n                            except:\n                                pt = 0.0\n                            resp_text = f"📥 *SITUAZIONE CAPITALE E RICAVI*\\n------------------------------------\\n💰 Versato Storico: *€{CAPITALE_VERSATO_TOTALE:.2f}*\\n\\n📈 Incasso di oggi (Netto): *+€{pt:.2f}*\\n------------------------------------\\n(Questo è il conteggio reale e netto da mezzanotte)."'
)

content = content.replace('**TOTALE PROTETTO**', 'TOTALE PROTETTO')

with open("/home/sergio/.openclaw/workspace/denaro/telegram_bot_interactive.py", "w") as f:
    f.write(content)
