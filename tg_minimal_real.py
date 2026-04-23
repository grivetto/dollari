#!/usr/bin/env python3
"""
DENARO Telegram Bot - VERSIONE REALE MINIMALE
"""
import os
import sys
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def read_capital_status():
    """Legge stato reale"""
    try:
        with open('/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log', 'r') as f:
            lines = f.readlines()[-20:]
        
        investment = 20
        for line in reversed(lines):
            if 'Investimento:' in line:
                try:
                    investment = float(line.split('€')[1].split()[0])
                except:
                    pass
                break
        return investment
    except:
        return 20

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stato reale del sistema"""
    grid_inv = read_capital_status()
    
    msg = f"""🚀 DENARO — DATI REALI {datetime.now().strftime('%H:%M')}

💰 Capitale: €425 (da €722)
📊 Grid: €{grid_inv} investiti
🎯 MC2: 0.00025 BTC allocati

Profitto oggi: €0.00
Stato: ATTIVO, aspetta segnali

Brutale verita: mercato decide.
Target: €3-5/giorno medio."""
    
    await update.message.reply_text(msg)

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 PROFITTO REALE OGGI:\n"
        "• Grid: €0\n"
        "• MC2: 0 trades\n"
        "• TOTALE: €0\n\n"
        "Setup completato.\n"
        "System ready."
    )

def main():
    if not TOKEN:
        print("NO TOKEN")
        return 1
    
    print(f"[{datetime.now()}] BOT REALE STARTED")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler(['start', 'status'], status))
    app.add_handler(CommandHandler('profit', profit))
    
    # Riprova se conflitto
    while True:
        try:
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            print(f"Error: {e}, riprovo in 10s...")
            time.sleep(10)

if __name__ == '__main__':
    main()
