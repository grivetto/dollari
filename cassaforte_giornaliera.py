#!/usr/bin/env python3
"""
CASSAFORTE GIORNALIERA — Chiusura giornata e salvataggio ricavi
Eseguito ogni giorno alle 23:59 via cron

Calcola:
1. Profitto/perdita giornaliera dai bot
2. Totale cassaforte accumulato
3. Invia report Telegram
"""

import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv('/home/sergio/denaro/.env')

logging.basicConfig(
    filename='/home/sergio/.openclaw/workspace/denaro/logs/cassaforte.log',
    level=logging.INFO,
    format='%(asctime)s - [CASSAFORTE] - %(message)s'
)

# File cassaforte
CASSAFORTE_FILE = '/home/sergio/.openclaw/workspace/denaro/cassaforte.json'
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID', '277954993')

class CassaforteGiornaliera:
    def __init__(self):
        self.data = self.load_cassaforte()
        self.oggi = datetime.now().strftime('%Y-%m-%d')
        
    def load_cassaforte(self):
        """Carica stato cassaforte"""
        if os.path.exists(CASSAFORTE_FILE):
            with open(CASSAFORTE_FILE) as f:
                return json.load(f)
        return {
            'totale_cassaforte': 0.0,
            'giorni_chiusi': [],
            'inizio': datetime.now().isoformat()
        }
    
    def save_cassaforte(self):
        """Salva stato cassaforte"""
        with open(CASSAFORTE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def calcola_profitto_giorno(self):
        """Calcola profitto giornaliero dai log"""
        profitto = 0.0
        
        # Leggi log Grid Bot — cerca pattern "Profit €X.XX"
        try:
            with open('/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if self.oggi in line and 'Profit' in line and '€' in line:
                        # Estrai solo il numero dopo €
                        try:
                            import re
                            match = re.search(r'€([\d.]+)', line)
                            if match:
                                profitto += float(match.group(1))
                        except:
                            pass
        except Exception as e:
            logging.warning(f"Errore lettura log Grid: {e}")
        
        return round(profitto, 2)
    
    def chiudi_giornata(self):
        """Esegue chiusura giornata"""
        logging.info(f"Chiusura giornata {self.oggi}")
        
        # Calcola profitto
        profitto_oggi = self.calcola_profitto_giorno()
        
        # Aggiungi a cassaforte (solo se positivo)
        if profitto_oggi > 0:
            self.data['totale_cassaforte'] += profitto_oggi
            logging.info(f"Profitto giorno: €{profitto_oggi} — AGGIUNTO a cassaforte")
        else:
            logging.info(f"Nessun profitto oggi (o perdita)")
        
        # Registra giorno
        giornata = {
            'data': self.oggi,
            'profitto': profitto_oggi,
            'cassaforte_totale': self.data['totale_cassaforte'],
            'chiuso': True
        }
        self.data['giorni_chiusi'].append(giornata)
        
        # Salva
        self.save_cassaforte()
        
        # Report
        self.invia_report(profitto_oggi)
        
        logging.info(f"Giornata chiusa. Cassaforte totale: €{self.data['totale_cassaforte']:.2f}")
    
    def invia_report(self, profitto_oggi):
        """Invia report Telegram"""
        try:
            if profitto_oggi > 0:
                emoji = "✅"
                stato = f"+€{profitto_oggi}"
            elif profitto_oggi < 0:
                emoji = "🔴"
                stato = f"€{profitto_oggi}"
            else:
                emoji = "⚪"
                stato = "€0.00"
            
            message = f"""{emoji} <b>CASSAFORTE GIORNALIERA</b>
<b>Data:</b> {self.oggi}
<b>Profitto Oggi:</b> {stato}
<b>Totale Cassaforte:</b> €{self.data['totale_cassaforte']:.2f}
<b>Giorni Operativi:</b> {len(self.data['giorni_chiusi'])}

💰 Denaro al sicuro — Giornata chiusa!"""
            
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            payload = {
                'chat_id': TG_CHAT,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, payload, timeout=10)
            logging.info("Report Telegram inviato")
            
        except Exception as e:
            logging.error(f"Errore invio Telegram: {e}")

if __name__ == "__main__":
    cassaforte = CassaforteGiornaliera()
    cassaforte.chiudi_giornata()
    print(f"✅ Cassaforte aggiornata: €{cassaforte.data['totale_cassaforte']:.2f}")
