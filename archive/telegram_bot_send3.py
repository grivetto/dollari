import gc
#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.telegram')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

msg = """🎯 **IL PACCHETTO "PRONTO-BOT" È PRONTO DA VENDERE A 39€/Mese!** 🎯

Sergio, ecco la "Lettera di Vendita" nuda e cruda che puoi usare per contattare a freddo (via mail o WhatsApp) gli artigiani di Torino. Leggila, copiala e girala agli idraulici:

--- COPIA E INCOLLA ---

Buongiorno,
Lavorando sul territorio di Torino, so bene che il problema principale di chi fa Pronto Intervento (idraulici, fabbri, elettricisti) è uno solo: **il telefono squilla mentre stai lavorando, non puoi rispondere, e il cliente chiama subito il tuo concorrente.**

Per risolvere questo problema ho creato un **Assistente WhatsApp Automatico** pensato esattamente per gli artigiani. 

Funziona in modo semplicissimo:
1. Quando non puoi rispondere, il cliente ti scrive su WhatsApp.
2. Il Bot risponde all'istante (H24) al posto tuo: *"Ciao! Sono l'assistente virtuale di [Tuo Nome]. Il tecnico ha le mani occupate, ma dimmi qual è l'emergenza!"*
3. Il Bot chiede in automatico al cliente **il problema, una FOTO del guasto e l'indirizzo**.
4. Tu ricevi una notifica silenziosa e ordinata sul tuo telefono con la foto del pezzo rotto e la via, pronto per fare il preventivo appena ti lavi le mani.

**Zero clienti persi, zero tempo perso al telefono per farti spiegare il guasto.**

Il servizio è "chiavi in mano": lo configuro io sul tuo numero aziendale e costa solo **39€ al mese** (praticamente si ripaga da solo salvando anche solo una mezza chiamata persa all'anno). Nessun vincolo, disdici quando vuoi.

Se ti interessa provarlo o vedere come funziona dal vivo, rispondimi a questo messaggio e ti faccio fare un test gratuito di 5 minuti.

Buon lavoro,
Sergio Grivetto
---

🛠️ *Nota tecnica per noi:*
Il sistema Python che ho appena montato nel tuo server (`workspace/pronto_bot/app.py`) è già in grado di ospitare illimitati numeri di telefono. Possiamo rivenderlo a 10 idraulici diversi e il mio codice gestirà tutte e 10 le chat contemporaneamente senza sbagliare una virgola! 🚀
"""

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})
print("sent")
