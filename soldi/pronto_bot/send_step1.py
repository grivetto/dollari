import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env.telegram')

TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_ID = os.getenv('WHATSAPP_PHONE_ID')
TO_PHONE = os.getenv('TARGET_PHONE')

url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

response_text = (
    "🤖 *Ciao! Sono l'assistente virtuale del Pronto Intervento.*\n\n"
    "Il tecnico in questo momento ha le mani occupate in un intervento, ma ci penso io a passargli la tua urgenza!\n"
    "👉 *Per poterti aiutare subito, descrivimi il problema in poche parole* (es. 'tubo rotto', 'caldaia bloccata', 'salvavita scatta')."
)

data = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": TO_PHONE,
    "type": "text",
    "text": {
        "body": response_text
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.text)
