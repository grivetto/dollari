import gc
#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.telegram')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

msg = """⚙️ **Come Configurare un Nuovo Cliente (Idraulico, Elettricista)** ⚙️

Sergio, se un artigiano ti dice "Lo compro, fammelo!", ecco i passaggi esatti che tu (e io) dobbiamo fare. Si divide in due fasi semplici:

### Fase 1: Lato Cliente (Sul suo telefono/PC)
Dobbiamo agganciare il SUO numero di telefono a Meta (Facebook). Ci vuole 1 minuto:
1. Gli chiedi di usare un numero di telefono (anche fisso o secondo numero aziendale) che *non ha già WhatsApp normale o Business attivo* sopra. (Se ce l'ha, deve cancellare l'app un attimo per liberare il numero).
2. Gli fai creare un account su **Meta Business Manager** (business.facebook.com).
3. Vai in "Account WhatsApp" > "Aggiungi numero". Meta gli manderà un SMS con un codice a 6 cifre al numero aziendale. Inseriscilo.
4. Ora vai su *Facebook Developers* (come abbiamo fatto per il test) e generi le sue **3 chiavi magiche**:
   - Token di Accesso Permanente (Sistema)
   - ID Numero di Telefono (Es. 1045332...)
   - WABA ID (WhatsApp Business Account ID)

### Fase 2: Lato Nostro (Sul tuo Server Linux)
Una volta che hai le sue chiavi, le passi a me. Io modificherò il file `app.py` aggiungendo un file `clienti.json` che farà da "Centralino Intelligente".

*Ecco come funzionerà il codice dietro le quinte:*
```json
{
  "1045332...": {
     "nome_artigiano": "Idraulico Marco",
     "whatsapp_token": "EAAxxx...",
     "telegram_chat_id": "999888777" // Il SUO account Telegram dove ricevere gli avvisi
  },
  "2033445...": {
     "nome_artigiano": "Elettrauto Giorgio",
     "whatsapp_token": "EAAyyy...",
     "telegram_chat_id": "444555666" // Il SUO account Telegram dove ricevere gli avvisi
  }
}
```

**Cosa fa il mio codice?**
Quando un utente scrive a Marco l'idraulico, Meta manda il webhook al nostro server. Il mio codice legge `1045332...` (l'ID di Marco), capisce che è lui, usa il *suo* Token per rispondere su WhatsApp e, alla fine del triage, manda la notifica push unicamente al *suo* Telegram ID (e non al tuo dei bot di trading, come nel test di prima!).

**Cosa devi fare fisicamente con l'artigiano:**
1. Ti fai dare 39€ al mese.
2. Ti fai dare un numero di telefono "pulito".
3. Gli fai scaricare l'app "Telegram" sul suo smartphone e gli dici di mandare "/start" a un bot Telegram che creeremo (es. `@ProntoInterventoTorinoBot`), così otteniamo il suo `telegram_chat_id`.
4. Mi passi i dati. Io compilo il JSON.

Lui si troverà i lead caldi sul telefono. Noi incassiamo l'abbonamento. Tutto automatico. 🚀
"""

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'})
print("sent")
