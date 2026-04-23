import gc
import qrcode
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

qr_data = ""
if not qr_data:
    print("No QR data found.")
    sys.exit(1)

qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(qr_data)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
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

body = "Ciao Sergio, ecco il QR code richiesto in formato immagine (.png) in allegato. Scansionalo con il tuo telefono per collegare Stella."
msg.attach(MIMEText(body, 'plain'))

with open("whatsapp_qr.png", 'rb') as f:
    img_data = f.read()
    image = MIMEImage(img_data, name="whatsapp_qr.png")
    msg.attach(image)

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, recipient, msg.as_string())
    print("Email con immagine inviata con successo!")
except Exception as e:
    print(f"Errore: {e}")
