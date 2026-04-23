#!/usr/bin/env python3
import os, asyncio, json, aiohttp
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8028848403:AAH2iPnginejNxDo4hFq_5xWnhEql3PVMPM')

async def get_nuvola_data():
    Legge dati dal Grid Bot su NUVOLA
    try:
        with open('/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log', 'r') as f:
            lines = f.readlines()[-20:]
        
        # Estrai ultimo investimento
        investment = 35  # Default
        orders = []
        for line in reversed(lines):
            if 'Investimento:' in line:
                try:
                    investment = float(line.split('€')[1].split()[0])
                except:
                    pass
                break
        
        # Conta ordini aperti
        for line in reversed(lines):
            if 'Grid piazzato:' in line:
                try:
                    num = line.split('Grid piazzato:')[1].split()[0]
                    return {'investment': investment, 'orders': num, 'status': 'running'}
                except:
                    pass
                break
        
        return {'investment': investment, 'orders': '3', 'status': 'running'}
    except Exception as e:
        return {'investment': 35, 'orders': '?', 'status': f'error: {e}'}

async def get_mc2_data():
    Legge dati dal Rebound Sniper su MC2
    try:
        with open('/home/sergio/denaro/status/positions_real.json', 'r') as f:
            positions = json.load(f)
        
        with open('/home/sergio/denaro/logs/rebound_real.log', 'r') as f:
            lines = f.readlines()[-30:]
        
        active = len([p for p in positions.values() if p.get('status') in ['hold', 'pending_buy']])
        pending_sell = len([p for p in positions.values() if p.get('status') == 'pending_sell'])
        
        # Cerca ultimo trade
        last_trade = None
        for line in reversed(lines):
            if 'BUY' in line and 'EXECUTED' in line:
                last_trade = 'BUY ' + line.split('BUY')[1].strip()[:30]
                break
            if 'CLOSED' in line and 'PNL' in line:
                last_trade = line.split('CLOSED')[1].strip()[:40]
                break
        
        return {
            'active_positions': active,
            'pending_sell': pending_sell,
            'last_trade': last_trade or 'No trades yet',
            'status': 'running'
        }
    except Exception as e:
        return {'active_positions': 0, 'pending_sell': 0, 'last_trade': 'No data', 'status': 'waiting'}

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Comando /status — mostra stato reale
    nuvola = await get_nuvola_data()
    mc2 = await get_mc2_data()
    
    message = f'''🚀 *DENARO SYSTEM — REAL DATA*

💰 *Capitale Allocato*
• NUVOLA (Grid): €{nuvola['investment']}
• MC2 (Rebound): Risk 0.2% BTC/trade

📊 *NUVOLA — Grid BTC/EUR*
Status: {nuvola['status']}
Ordini aperti: {nuvola['orders']} BUY
Attesa: BTC scenda a ~€57k

🎯 *MC2 — Rebound Sniper*
Status: {mc2['status']}
Posizioni attive: {mc2['active_positions']}
In chiusura: {mc2['pending_sell']}
Ultimo: {mc2['last_trade']}

⏰ Aggiornato: {datetime.now().strftime('%H:%M:%S')}'''
    
    keyboard = [
        [InlineKeyboardButton('🔄 Aggiorna', callback_data='refresh')],
        [InlineKeyboardButton('📈 MC2 Log', callback_data='mc2_log'),
         InlineKeyboardButton('📊 NUVOLA Log', callback_data='nuvola_log')]
    ]
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'refresh':
        await status(update, context)
    elif query.data == 'mc2_log':
        try:
            with open('/home/sergio/denaro/logs/rebound_real.log', 'r') as f:
                lines = f.readlines()[-15:]
            log_text = ''.join(lines)[-3500:]
            await query.edit_message_text(f'*MC2 Log (ultime righe):*\n', parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(f'Errore lettura log: {e}')
    elif query.data == 'nuvola_log':
        try:
            with open('/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log', 'r') as f:
                lines = f.readlines()[-15:]
            log_text = ''.join(lines)[-3500:]
            await query.edit_message_text(f'*NUVOLA Log (ultime righe):*\n', parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(f'Errore lettura log: {e}')

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    Comando /profit — calcola P
