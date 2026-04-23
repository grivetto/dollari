import gc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Credenziali Sergio (da USER.md)
SMTP_SERVER = "smtps.aruba.it"
SMTP_PORT = 465
SMTP_USER = "sergio@grivetto.eu"
SMTP_PASS = "@Romeo_2030"

recipient = "sergio@grivetto.eu"
subject = "QR Code WhatsApp per Stella"

with open("qr_whatsapp.txt", "r") as f:
    qr_content = f.read()

msg = MIMEMultipart()
msg['From'] = SMTP_USER
msg['To'] = recipient
msg['Subject'] = subject

body = f"""Ciao Sergio,

Ecco il QR code aggiornato per collegare Stella a WhatsApp.
Aprilo sul PC o su un altro dispositivo e scanzionalo con il tuo telefono principale.

{qr_content}

Fammi sapere quando hai fatto!
Stella 👩‍💻"""

msg.attach(MIMEText(body, 'plain'))

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, recipient, msg.as_string())
    print("Email inviata con successo!")
except Exception as e:
    print(f"Errore durante l'invio dell'email: {e}")
