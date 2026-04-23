import gc
import json
import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

# Try to find the QR string in the JSON output
qr_string = None
try:
    with open("qr_json.txt", "r") as f:
        for line in f:
            try:
                data = json.loads(line)
                # Looking for a structure like {"type":"qr","data":"..."}
                if data.get("type") == "qr":
                    qr_string = data.get("data")
                    break
            except:
                # Wacli also outputs "2@..." strings directly in some versions
                if "2@" in line:
                    import re
                    match = re.search(r'2@[^ \"]*', line)
                    if match:
                        qr_string = match.group(0)
                        break
except Exception as e:
    print(f"Error reading JSON: {e}")

if not qr_string:
    print("Could not find QR string.")
    # Exit silently or with error
    exit(1)

# Generate image
img = qrcode.make(qr_string)
img.save("whatsapp_qr.png")

# Email credentials (from USER.md)
SMTP_SERVER = "smtps.aruba.it"
SMTP_PORT = 465
SMTP_USER = "sergio@grivetto.eu"
SMTP_PASS = "@Romeo_2030"

recipient = "sergio@grivetto.eu"
msg = MIMEMultipart()
msg['From'] = SMTP_USER
msg['To'] = recipient
msg['Subject'] = "Immagine QR Code WhatsApp per Stella"

body = "Ciao Sergio, ecco il QR code in formato immagine allegato. Scansionalo con WhatsApp."
msg.attach(MIMEText(body, 'plain'))

with open("whatsapp_qr.png", 'rb') as f:
    img_data = f.read()
    image = MIMEImage(img_data, name="whatsapp_qr.png")
    msg.attach(image)

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, recipient, msg.as_string())
    print("Email con immagine inviata!")
except Exception as e:
    print(f"Errore email: {e}")
