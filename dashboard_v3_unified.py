#!/usr/bin/env python3
"""
DASHBOARD DENARO V3 — Unica per Nuvola e MC2
Valori REALI da Binance + stato di entrambi i bot
"""

import os
import json
import ccxt
import subprocess
from datetime import datetime
from flask import Flask

from dotenv import load_dotenv
load_dotenv('/home/sergio/.openclaw/workspace/denaro/.env')

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
        eth_free = bal.get('ETH', {}).get('free', 0)
        eth_locked = bal.get('ETH', {}).get('locked', 0)
        btc_free = bal.get('BTC', {}).get('free', 0)
        bnb_free = bal.get('BNB', {}).get('free', 0)
        sol_free = bal.get('SOL', {}).get('free', 0)
        
        btc_price = ex.fetch_ticker('BTC/EUR')['last']
        eth_price = ex.fetch_ticker('ETH/EUR')['last']
        bnb_price = ex.fetch_ticker('BNB/EUR')['last'] if 'BNB/EUR' in [m['symbol'] for m in ex.fetch_markets()] else 0
        
        total_eur = 0
        try:
            for b in bal['info'].get('balances', []):
                f = float(b.get('free', 0))
                l = float(b.get('locked', 0))
                val = f + l
                if val <= 0: continue
                
                asset = b['asset']
                if asset == 'EUR':
                    total_eur += val
                else:
                    try:
                        pair = f"{asset}/EUR"
                        if pair in ex.symbols:
                            price = ex.fetch_ticker(pair)['last']
                            total_eur += val * price
                    except:
                        pass # Ignore dust
        except Exception as e:
            err_msg = f"Error calculating total: {e}"

        
        pnl = total_eur - CAPITALE_INIZIALE
        
        orders = ex.fetch_open_orders('ETH/EUR')
        buy_orders = [{'price': o['price'], 'amount': o['amount']} for o in orders if o['side'] == 'buy']
        sell_orders = [{'price': o['price'], 'amount': o['amount']} for o in orders if o['side'] == 'sell']
        
        return {
            'total_eur': round(total_eur, 2),
            'pnl': round(pnl, 2),
            'pnl_pct': round((pnl / CAPITALE_INIZIALE) * 100, 2),
            'eur_free': round(eur_free, 2),
            'eth_free': round(eth_free, 5),
            'eth_locked': round(eth_locked, 5),
            'eth_price': eth_price,
            'bnb_free': round(bnb_free, 4),
            'bnb_price': bnb_price,
            'btc_free': round(btc_free, 6),
            'btc_price': btc_price,
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
        }
    except Exception as e:
        return {'error': str(e)}

def get_nuvola_grid_status():
    """Stato Grid Bot V2 su Nuvola"""
    status = {'active': False, 'logs': [], 'pid': None}
    try:
        result = subprocess.run(['pgrep', '-f', 'grid_bot_v2'], capture_output=True, text=True)
        if result.stdout.strip():
            status['active'] = True
            status['pid'] = result.stdout.strip()
        
        log_file = '/home/sergio/.openclaw/workspace/denaro/grid_bot_v2.log'
        if os.path.exists(log_file):
            result = subprocess.run(['tail', '-n', '15', log_file], capture_output=True, text=True)
            status['logs'] = [line.strip() for line in result.stdout.strip().split('\n')[-8:] if line.strip()]
        
        # Get open orders for grid display
        ex = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'enableRateLimit': True,
        })
        orders = ex.fetch_open_orders('ETH/EUR')
        status['orders'] = [{'side': o['side'], 'price': o['price'], 'amount': o['amount']} for o in orders]
    except:
        pass
    return status

def get_mc2_sniper_status():
    """Stato Sniper V2 su MC2 via SSH"""
    status = {'active': False, 'logs': [], 'positions': {}, 'pnl': 0}
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
             '-p', '2222', 'sergio@93.43.252.114',
             'ps aux | grep sniper_v2 | grep -v grep | wc -l'],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip() == '1' or result.stdout.strip() == '2':
            status['active'] = True
        
        # Get sniper log
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
             '-p', '2222', 'sergio@93.43.252.114',
             'tail -n 20 ~/denaro/logs/sniper_v2.log 2>/dev/null || echo NO_LOG'],
            capture_output=True, text=True, timeout=15
        )
        status['logs'] = [line.strip() for line in result.stdout.strip().split('\n')[-10:] if line.strip() and line.strip() != 'NO_LOG']
        
        # Get positions file
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
             '-p', '2222', 'sergio@93.43.252.114',
             'cat ~/denaro/status/sniper_positions.json 2>/dev/null || echo {}'],
            capture_output=True, text=True, timeout=15
        )
        try:
            pos_data = json.loads(result.stdout.strip() or '{}')
            status['positions'] = pos_data.get('positions', {})
            status['pnl'] = pos_data.get('total_pnl', 0)
        except:
            pass
            
    except Exception as e:
        status['error'] = str(e)
    return status

@app.route('/')
def index():
    binance = get_binance_data()
    grid = get_nuvola_grid_status()
    sniper = get_mc2_sniper_status()
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Build orders table
    buy_rows = ''.join([f'<tr style="color:#0f0"><td>BUY</td><td>€{o["price"]:,.2f}</td><td>{o["amount"]:.4f} ETH</td></tr>' for o in grid.get('orders', []) if o['side'] == 'buy'])
    sell_rows = ''.join([f'<tr style="color:#f44"><td>SELL</td><td>€{o["price"]:,.2f}</td><td>{o["amount"]:.4f} ETH</td></tr>' for o in grid.get('orders', []) if o['side'] == 'sell'])
    
    # Build sniper positions
    pos_rows = ''
    for sym, pos in sniper.get('positions', {}).items():
        color = '#ff0' if pos.get('status') == 'holding' else '#0f0' if 'buy' in pos.get('status', '') else '#f44'
        pos_rows += f'<tr style="color:{color}"><td>{sym}</td><td>{pos.get("status","?")}</td><td>€{pos.get("entry_price", pos.get("target_price", "N/A"))}</td><td>{pos.get("amount", "N/A")}</td></tr>'
    
    # Build sniper logs
    sniper_logs = ''.join([f'<p style="font-size:11px;margin:2px 0;color:#ccc">{l}</p>' for l in sniper['logs'][-6:]])
    grid_logs = ''.join([f'<p style="font-size:11px;margin:2px 0;color:#ccc">{l}</p>' for l in grid['logs'][-6:]])
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Denaro Dashboard V3</title>
    <meta http-equiv="refresh" content="60">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family: 'Courier New', monospace; background:#0a0a0a; color:#e0e0e0; padding:20px; }}
        h1 {{ color:#0f0; font-size:24px; margin-bottom:10px; }}
        h2 {{ color:#0f0; font-size:18px; margin:15px 0 10px; border-bottom:1px solid #333; padding-bottom:5px; }}
        .container {{ max-width:1200px; margin:0 auto; }}
        .row {{ display:flex; gap:20px; flex-wrap:wrap; }}
        .box {{ background:#111; border:1px solid #333; border-radius:8px; padding:15px; flex:1; min-width:300px; }}
        .big {{ font-size:36px; color:#0f0; }}
        .red {{ color:#f44; }}
        .green {{ color:#0f0; }}
        .yellow {{ color:#ff0; }}
        .dim {{ color:#666; }}
        table {{ width:100%; border-collapse:collapse; margin:10px 0; }}
        td {{ padding:4px 8px; border-bottom:1px solid #222; font-size:13px; }}
        .status-dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:8px; }}
        .online {{ background:#0f0; box-shadow:0 0 5px #0f0; }}
        .offline {{ background:#f00; }}
        .logs {{ background:#000; padding:10px; border-radius:4px; max-height:200px; overflow-y:auto; }}
        @media(max-width:768px) {{ .row {{ flex-direction:column; }} }}
    </style>
</head>
<body>
<div class="container">
    <h1>💰 DENARO DASHBOARD V3</h1>
    <p class="dim">Ultimo aggiormamento: {now} | Capacite iniziale: €{CAPITALE_INIZIALE:.2f}</p>
    
    <div class="row" style="margin:15px 0">
        <div class="box" style="text-align:center">
            <h2>PORTAFOGLIO</h2>
            <div class="{'big' if binance.get('total_eur',0)>0 else 'red'}">€{binance.get('total_eur', 0):,.2f}</div>
            <p>PnL: <span class="{'green' if binance.get('pnl',0)>=0 else 'red'}">€{binance.get('pnl', 0):,.2f} ({binance.get('pnl_pct', 0):.1f}%)</span></p>
        </div>
        <div class="box" style="text-align:center">
            <h2>COMPOSIZIONE</h2>
            <p style="font-size:16px">EUR liberi: <span class="green">€{binance.get('eur_free', 0):,.2f}</span></p>
            <p>ETH: {binance.get('eth_free', 0):.4f} ≈ €{binance.get('eth_free', 0) * binance.get('eth_price', 0):.2f}</p>
            <p>BNB: {binance.get('bnb_free', 0):.4f} ≈ €{binance.get('bnb_free', 0) * binance.get('bnb_price', 0):.2f}</p>
            <p class="dim">ETH locked: {binance.get('eth_locked', 0):.4f} | BTC: {binance.get('btc_free', 0):.6f}</p>
            <p class="dim">ETH: €{binance.get('eth_price', 0):,.2f} | BTC: €{binance.get('btc_price', 0):,.2f}</p>
        </div>
    </div>
    
    <div class="row">
        <div class="box">
            <h2><span class="status-dot {'online' if grid['active'] else 'offline'}"></span>NUVOLA — Grid Bot V2</h2>
            <p>Status: {'<span class="green">ATTIVO</span>' if grid['active'] else '<span class="red">NON ATTIVO</span>'} {f"(PID: {grid['pid']})" if grid.get('pid') else ''}</p>
            
            <h3 style="margin:10px 0 5px; color:#888">ORDINI APERTI</h3>
            <table>
                <tr><th>LATO</th><th>PREZZO</th><th>AMOUNT</th></tr>
                {buy_rows if buy_rows else '<tr><td colspan="3" style="text-align:center;color:#666">Nessun ordine</td></tr>'}
                {sell_rows if sell_rows else ''}
            </table>
            
            <h3 style="margin:10px 0 5px; color:#888">LOG</h3>
            <div class="logs">{grid_logs or '<p style="color:#666">Nessun log</p>'}</div>
        </div>
        
        <div class="box">
            <h2><span class="status-dot {'online' if sniper['active'] else 'offline'}"></span>MC2 — Sniper V2</h2>
            <p>Status: {'<span class="green">ATTIVO</span>' if sniper['active'] else '<span class="red">NON ATTIVO</span>'}</p>
            <p>PnL Sniper: <span class="{'green' if sniper.get('pnl',0)>=0 else 'red'}">€{sniper.get('pnl', 0):.2f}</span></p>
            
            <h3 style="margin:10px 0 5px; color:#888">POSIZIONI APERTE</h3>
            <table>
                <tr><th>PAIR</th><th>STATO</th><th>ENTRY</th><th>AMOUNT</th></tr>
                {pos_rows if pos_rows else '<tr><td colspan="4" style="text-align:center;color:#666">Nessuna posizione</td></tr>'}
            </table>
            
            <h3 style="margin:10px 0 5px; color:#888">LOG</h3>
            <div class="logs">{sniper_logs or '<p style="color:#666">Nessun log</p>'}</div>
        </div>
    </div>
    
    <p class="dim" style="margin-top:20px;text-align:center">sgrivett.ddns.net:8443 | Aggiornamento automatico ogni 60s</p>
</div>
</body>
</html>'''
    
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
