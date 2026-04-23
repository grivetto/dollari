import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env.telegram')

sender_email = "sergio@grivetto.eu"
receiver_email = "sergio.grivetto@gmail.com" 
password = "@Romeo_2030"

# --- Contenuto HTML Professionale ---
html_body = f"""\
<html>
  <body style="font-family: 'Inter', Arial, sans-serif; color: #333333; line-height: 1.6;">
    <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #dddddd; border-radius: 8px; background-color: #ffffff;">
      <div style="background-color: #10B981; color: white; padding: 15px; text-align: center; border-radius: 6px 6px 0 0;">
        <h2 style="margin: 0; font-weight: 800;">PRONTOMATIC: Il Tuo Assistente WhatsApp H24</h2>
      </div>
      <div style="padding: 25px 20px;">
        <p>Gentile Professionista,</p>
        <p>Capisco che il tuo tempo è oro, specialmente quando sei nel mezzo di un intervento a Torino. Ogni squillo perso è un potenziale cliente che chiama il concorrente.</p>
        
        <div style="border-left: 3px solid #10B981; padding-left: 15px; margin: 20px 0; background-color: #f9f9f9; border-radius: 4px;">
            <p style="font-weight: 600; color: #374151;">Il tuo problema risolto da <strong>PRONTOMATIC</strong>:</p>
            <ul style="margin-top: 5px; padding-left: 20px;">
                <li>Risposta Immediata 24/7 (mai più clienti persi).</li>
                <li>Qualificazione automatica: **chiede problema, foto e indirizzo.**</li>
                <li>Notifiche pulite sul tuo Telegram per decidere l'intervento.</li>
            </ul>
        </div>

        <p>Il servizio è **chiavi in mano** e costa solo:</p>
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 28px; font-weight: 900; color: #EF4444;">€10</span>
            <span style="font-size: 16px; font-weight: 600; color: #4B5563;">/ mese</span>
            <span style="display: block; font-size: 12px; margin-top: 5px;">(Setup una tantum: €25)</span>
        </div>

        <p style="text-align: center; margin-top: 30px;">
            <a href="https://api.whatsapp.com/send?phone=393711741209&text=Demo%20ProntoMatic" 
               style="background-color: #25D366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
               Clicca qui per una Demo su WhatsApp (30 secondi)
            </a>
        </p>

        <p style="margin-top: 30px; font-size: 12px; color: #999999;">
            Cordiali saluti,<br>
            Stella - Collaboratrice Tecnica
        </p>
      </div>
    </div>
  </body>
</html>
"""

message = MIMEMultipart("alternative")
message["Subject"] = "PROPOSTA: Automatizza i tuoi clienti con PRONTOMATIC (Solo 10€/Mese)"
message["From"] = sender_email
message["To"] = receiver_email

part = MIMEText(html_body, "html")
message.attach(part)

try:
    with smtplib.SMTP_SSL("smtps.aruba.it", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("HTML Sales pitch email sent successfully.")
except Exception as e:
    print(f"Error sending HTML sales pitch email: {e}")
