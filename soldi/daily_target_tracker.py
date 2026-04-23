#!/usr/bin/env python3
"""
Daily Target Tracker — Monitora se raggiungiamo €3-5/giorno
Invia alert Telegram se sotto/sopra target
"""

import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env.telegram')

logging.basicConfig(
    filename='TARGET_TRACKER.log',
    level=logging.INFO,
    format='%(asctime)s - [TRACKER] - %(message)s'
)

class DailyTargetTracker:
    def __init__(self):
        self.tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.tg_chat = os.getenv('TELEGRAM_CHAT_ID', '277954993')
        self.state_file = '/home/sergio/.openclaw/workspace/denaro/daily_target_state.json'
        self.capital_file = '/home/sergio/.openclaw/workspace/denaro/capital_state.json'
        
        # Target progressivi
        self.targets = {
            1: 3.0,   # Fase 1: €3/giorno
            2: 5.0,   # Fase 2: €5/giorno  
            3: 8.0,   # Fase 3: €8/giorno
            4: 10.0   # Fase 4: €10/giorno
        }
        
        self.current_phase = self.detect_phase()
        self.daily_target = self.targets[self.current_phase]
        
    def detect_phase(self):
        """Rileva fase in base al capitale"""
        try:
            if os.path.exists(self.capital_file):
                with open(self.capital_file) as f:
                    data = json.load(f)
                    capital = data.get('current', 425)
                    
                    if capital >= 800:
                        return 4
                    elif capital >= 650:
                        return 3
                    elif capital >= 500:
                        return 2
                    else:
                        return 1
            return 1
        except:
            return 1
    
    def send_telegram(self, message):
        """Invia messaggio Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
            payload = {
                'chat_id': self.tg_chat,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, payload, timeout=10)
        except Exception as e:
            logging.error(f"Errore Telegram: {e}")
    
    def check_daily_progress(self):
        """Controlla progresso giornaliero"""
        try:
            # Leggi stato capitale
            if not os.path.exists(self.capital_file):
                return
                
            with open(self.capital_file) as f:
                capital_data = json.load(f)
            
            history = capital_data.get('daily_history', [])
            if not history:
                return
            
            today_data = history[-1]
            today_pnl = today_data.get('pnl', 0)
            
            # Calcola percentuale target raggiunto
            progress = (today_pnl / self.daily_target) * 100
            
            # Report ore 12:00 (metà giornata)
            now = datetime.now()
            if now.hour == 12 and now.minute < 5:
                if progress < 30:
                    msg = (f"⚠️ <b>Sotto target a metà giornata</b>\n"
                           f"P&L: €{today_pnl:.2f} / €{self.daily_target:.2f} ({progress:.0f}%)\n"
                           f"Fase: {self.current_phase} | Capitale: €{capital_data.get('current', 0):.2f}")
                    self.send_telegram(msg)
                    logging.warning(f"Alert metà giornata: {progress:.0f}%")
            
            # Report ore 23:00 (fine giornata)
            if now.hour == 23 and now.minute < 5:
                if today_pnl >= self.daily_target:
                    emoji = "✅"
                    status = "TARGET RAGGIUNTO"
                elif today_pnl >= self.daily_target * 0.5:
                    emoji = "🟡"
                    status = "Meta target"
                else:
                    emoji = "🔴"
                    status = "Sotto target"
                
                msg = (f"{emoji} <b>Report Giornaliero</b>\n\n"
                       f"<b>Status:</b> {status}\n"
                       f"<b>P&L Oggi:</b> €{today_pnl:.2f}\n"
                       f"<b>Target:</b> €{self.daily_target:.2f} ({progress:.0f}%)\n"
                       f"<b>Capitale:</b> €{capital_data.get('current', 0):.2f}\n"
                       f"<b>Fase:</b> {self.current_phase}/4\n\n"
                       f"Totale profitti: €{capital_data.get('total_profit', 0):.2f}")
                
                self.send_telegram(msg)
                logging.info(f"Report fine giornata: €{today_pnl:.2f}")
                
                # Se target raggiunto per 3 giorni, suggerisci upgrade
                if len(history) >= 3:
                    last_3 = history[-3:]
                    if all(h.get('pnl', 0) >= self.daily_target * 0.8 for h in last_3):
                        new_phase = min(self.current_phase + 1, 4)
                        if new_phase > self.current_phase:
                            self.send_telegram(
                                f"🚀 <b>Pronto per Fase {new_phase}!</b>\n"
                                f"Target giornaliero: €{self.targets[new_phase]:.0f}"
                            )
                
        except Exception as e:
            logging.error(f"Errore check: {e}")
    
    def run(self):
        """Loop principale — ogni 5 minuti"""
        logging.info(f"🎯 Daily Target Tracker avviato — Fase {self.current_phase}")
        logging.info(f"💰 Target giornaliero: €{self.daily_target}")
        
        while True:
            try:
                self.check_daily_progress()
                import time
                time.sleep(300)  # 5 minuti
            except Exception as e:
                logging.error(f"Errore: {e}")
                time.sleep(60)

if __name__ == "__main__":
    tracker = DailyTargetTracker()
    tracker.run()
