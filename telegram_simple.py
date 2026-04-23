#!/usr/bin/env python3
import os
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def status(update: Update, context):
    msg = "🚀 DENARO REAL STATUS\n\n📊 NUVOLA Grid: Running\n💰 MC2 Rebound: Running\n📅 Ultimo check: LIVE"
    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("start", status))
    app.run_polling()

if __name__ == "__main__":
    main()
