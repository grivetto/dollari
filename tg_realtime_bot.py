#!/usr/bin/env python3
import os
import asyncio
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def read_nuvola_status():
    try:
        with open('/home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log', 'r') as f:
            lines = f.readlines()[-30:]
        
        investment = 35
        orders = '3'
        range_price = 'N/A'
        
        for line in reversed(lines):
            if 'Investimento:' in line:
                try:
                    investment = line.split('€')[1].split()[0]
                except:
                    pass
                break
        
        for line in reversed(lines):
            if 'Grid piazzato:' in line:
                try:
                    parts = line.split('Grid piazzato:')[1].split('|')
                    orders = parts[0].strip()
                    if 'Range:' in line:
                        range_price = line.split('Range:')[1].strip()
                except:
                    pass
                break
        
        return {'investment': investment, 'orders': orders, 'range': range_price, 'status': '✅ Running'}
    except Exception as e:
        return {'investment': 35, 'orders': '?', 'range': 'N/A', 'status': f'⚠️ Error: {str(e)[:20]}'}

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nuvola = read_nuvola_status()
    
    message = f🚀 *DENARO SYSTEM — REAL DATA*
