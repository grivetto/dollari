#!/bin/bash
# Script per avviare il Trading Bot
# Uso: ./run_bot.sh

cd /home/sergio/.openclaw/workspace/denaro
source trading_bot_env/bin/activate
python binance_trading_bot.py
