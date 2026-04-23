#!/usr/bin/env python3
"""
DASHBOARD DENARO — Valori REALI da Binance
Aggiornamento automatico al refresh della pagina
"""

import os
import json
import ccxt
import subprocess
from datetime import datetime
from flask import Flask
from dotenv import load_dotenv

load_dotenv('/home/sergio/denaro/.env')

app = Flask(__name__)
CAPITALE_INIZIALE = 722.00

def get_binance_data():
    """Legge saldo REALE da Binance"""
    try:
        ex = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        
        bal = ex.fetch_balance()
        
        eur_free = bal.get('EUR', {}).get('free', 0)
        eur_used = bal.get('EUR', {}).get('used', 0)
        usdt_free = bal.get('USDT', {}).get('free', 0)
        btc_free = bal.get('BTC', {}).get('free', 0)
        eth_free = bal.get('ETH', {}).get('free', 0)
        
        btc_price = ex.fetch_ticker('BTC/EUR')['last']
        eth_price = ex.fetch_ticker('ETH/EUR')['last']
        
        total_eur = eur_free + eur_used + usdt_free + (btc_free * btc_price) + (eth_free * eth_price)
        pnl = total_eur - CAPITALE_INIZIALE
        
        # Open orders
        orders = ex.fetch_open_orders('ETH/EUR')
        buy_orders = [o for o in orders if o['side'] == 'buy']
        sell_orders = [o for o in orders if o['side'] == 'sell']
        
        return {
            'total_eur': round(total_eur, 2),
            'pnl': round(pnl, 2),
            'pnl_pct': round((pnl / CAPITALE_INIZIALE) * 100, 2),
            'eur_free': round(eur_free, 2),
            'btc': round(btc_free, 6),
            'btc_eur': round(btc_free * btc_price, 2),
            'eth': round(eth_free, 5),
            'eth_eur': round(eth_free * eth_price, 2),
            'usdt': round(usdt_free, 2),
            'btc_price': btc_price,
            'eth_price': eth_price,
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
        }
    except Exception as e:
        return {'error': str(e)}

def get_grid_status():
    """Stato Grid Bot"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'grid_bot_v2'],
                              capture_output=True, text=True)
        active = result.stdout.strip() == 'active'
        
        log_file = '/home/sergio/.openclaw/workspace/denaro/grid_bot_v2.log'
        last_logs = []
        if os.path.exists(log_file):
            result = subprocess.run(['tail', '-n', '5', log_file],
                                  capture_output=True, text=True)
            for line in result.stdout.strip().split('\n')[-3:]:
                if ' - ' in line:
                    last_logs.append(line.split(' - ', 2)[-1])
        
        return {'active': active, 'logs': last_logs}
    except:
        return {'active': False, 'logs': []}

def get_mc2_status():
    """Stato MC2 via SSH"""
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=3', '-o', 'StrictHostKeyChecking=no',
             '-p', '2222', '-i', os.path.expanduser('~/.ssh/id_ed25519'),
             'sergio@93.43.252.114', 'tail -n 10 ~/denaro/logs/sniper_v2.log'],
            capture_output=True, text=True, timeout=10
        )
        logs = []
        for line in result.stdout.strip().split('\n')[-3:]:
            if ' - ' in line:
                logs.append(line.split(' - ', 2)[-1])
        return {'active': result.returncode == 0, 'logs': logs}
    except:
        return {'active': False, 'logs': []}

@app.route('/')
def dashboard():
    data = get_binance_data()
    grid = get_grid_status()
    mc2 = get_mc2_status()
    now = datetime.now().strftime('%H:%M:%S — %d/%m/%Y')
    
    if 'error' in data:
        return f"<h1>Errore connessione Binance: {data['error']}</h1>"
    
    pnl_color = "#16c784" if data['pnl'] >= 0 else "#ea3943"
    pnl_sign = "+" if data['pnl'] >= 0 else ""
    
    grid_status = "<span style='color:#16c784'>✅ ATTIVO</span>" if grid['active'] else "<span style='color:#ea3943'>❌ INATTIVO</span>"
    mc2_status = "<span style='color:#16c784'>✅ ATTIVO</span>" if mc2['active'] else "<span style='color:#ea3943'>❌ INATTIVO</span>"
    
    orders_html = ""
    for log in grid['logs']:
        orders_html += f"<div style='padding:4px 8px;margin:2px 0;background:rgba(255,255,255,0.05);border-radius:4px;font-size:12px;font-family:monospace;'>{log}</div>"
    
    mc2_html = ""
    for log in mc2['logs']:
        mc2_html += f"<div style='padding:4px 8px;margin:2px 0;background:rgba(255,255,255,0.05);border-radius:4px;font-size:12px;font-family:monospace;'>{log}</div>"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <title>DENARO Dashboard Reale</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0d1117; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ text-align: center; margin-bottom: 10px; font-size: 1.5em; }}
        .subtitle {{ text-align: center; color: #8b949e; font-size: 0.85em; margin-bottom: 25px; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; margin-bottom: 15px; }}
        .card h2 {{ color: #58a6ff; font-size: 1.1em; margin-bottom: 12px; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }}
        .stat {{ background: #0d1117; padding: 12px; border-radius: 6px; text-align: center; }}
        .stat .label {{ color: #8b949e; font-size: 0.75em; text-transform: uppercase; margin-bottom: 4px; }}
        .stat .value {{ font-size: 1.3em; font-weight: bold; }}
        .pnl-positive {{ color: #16c784; }}
        .pnl-negative {{ color: #ea3943; }}
        .log-box {{ max-height: 150px; overflow-y: auto; margin-top: 8px; }}
        .refresh {{ text-align: center; color: #8b949e; font-size: 0.75em; margin-top: 15px; }}
    </style>
</head>
<body>
<div class="container">
    <h1>💰 DENARO — Dashboard Reale</h1>
    <div class="subtitle">Dati live da Binance | Aggiornamento: {now}</div>
    
    <div class="card">
        <h2>🏦 Portafoglio Binance (Valore Reale)</h2>
        <div class="stat-grid">
            <div class="stat">
                <div class="label">Totale</div>
                <div class="value" style="color:#58a6ff">€{data['total_eur']:.2f}</div>
            </div>
            <div class="stat">
                <div class="label">Profitto/PNL</div>
                <div class="value {('pnl-positive' if data['pnl']>=0 else 'pnl-negative')}">{pnl_sign}€{data['pnl']:.2f} ({pnl_sign}{data['pnl_pct']}%)</div>
            </div>
            <div class="stat">
                <div class="label">BTC Prezzo</div>
                <div class="value">€{data['btc_price']:,.0f}</div>
            </div>
            <div class="stat">
                <div class="label">ETH Prezzo</div>
                <div class="value">€{data['eth_price']:,.0f}</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>📊 Dettaglio Asset</h2>
        <div class="stat-grid">
            <div class="stat">
                <div class="label">EUR Libero</div>
                <div class="value">€{data['eur_free']:.2f}</div>
            </div>
            <div class="stat">
                <div class="label">BTC ({data['btc']:.6f})</div>
                <div class="value">€{data['btc_eur']:.2f}</div>
            </div>
            <div class="stat">
                <div class="label">ETH ({data['eth']:.5f})</div>
                <div class="value">€{data['eth_eur']:.2f}</div>
            </div>
            <div class="stat">
                <div class="label">USDT</div>
                <div class="value">${data['usdt']:.2f}</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>🤖 Stato Grid Bot (ETH/EUR)</h2>
        <div class="stat-grid">
            <div class="stat">
                <div class="label">Status</div>
                <div>{grid_status}</div>
            </div>
            <div class="stat">
                <div class="label">Ordini BUY</div>
                <div class="value">{data['buy_orders']}</div>
            </div>
            <div class="stat">
                <div class="label">Ordini SELL</div>
                <div class="value">{data['sell_orders']}</div>
            </div>
        </div>
        <div class="log-box">{orders_html}</div>
    </div>
    
    <div class="card">
        <h2>🎯 Rebound Sniper (MC2)</h2>
        <div class="stat">
            <div class="label">Status MC2</div>
            <div>{mc2_status}</div>
        </div>
        <div class="log-box">{mc2_html}</div>
    </div>
    
    <div class="refresh">Auto-refresh ogni 60 secondi | sgrivett.ddns.net:8443</div>
</div>
</body>
</html>"""
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
