import gc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "sergio@grivetto.eu"
receiver_email = "sergio.grivetto@gmail.com"
password = "@Romeo_2030"

message = MIMEMultipart("alternative")
message["Subject"] = "Test Email Corretto - Amica (OpenClaw)"
message["From"] = sender_email
message["To"] = receiver_email

text = """\
Ciao Sergio,

Questo è il messaggio di test inviato all'indirizzo corretto dalla tua collaboratrice virtuale (Amica).
Il server SMTP di Aruba è configurato e funzionante!

Buon proseguimento,
Amica
"""
part = MIMEText(text, "plain")
message.attach(part)

try:
    with smtplib.SMTP_SSL("smtps.aruba.it", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully.")
except Exception as e:
    print(f"Error sending email: {e}")
