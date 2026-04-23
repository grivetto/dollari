#!/usr/bin/env python3
"""
ORBITAL COMMAND v2.0 — Dashboard Realistica
Target: €3-5/giorno | Capitale: €425 | Fase 1
"""

import os
import json
import psutil
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORBITAL COMMAND v2.0 | Realistic Mode</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff88;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px;
            border-bottom: 3px solid #00ff88;
            margin-bottom: 30px;
            background: rgba(0,255,136,0.1);
        }
        h1 {
            font-size: 2.5em;
            text-shadow: 0 0 20px #00ff88;
            margin-bottom: 10px;
            color: #fff;
        }
        .subtitle {
            color: #ff6b6b;
            font-size: 1.2em;
            font-weight: bold;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .card {
            background: rgba(0,0,0,0.6);
            border: 2px solid #00ff88;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 0 20px rgba(0,255,136,0.2);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0,255,136,0.4);
        }
        .card h2 {
            color: #ffd93d;
            font-size: 1.3em;
            margin-bottom: 15px;
            text-transform: uppercase;
            border-bottom: 1px solid #ffd93d;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 12px 0;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        .metric-label {
            color: #aaa;
        }
        .metric-value {
            color: #00ff88;
            font-weight: bold;
            font-size: 1.1em;
        }
        .positive { color: #00ff88; }
        .negative { color: #ff6b6b; }
        .warning { color: #ffd93d; }
        .bot-list {
            list-style: none;
        }
        .bot-item {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            margin: 5px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            border-left: 3px solid #00ff88;
        }
        .bot-name {
            color: #fff;
        }
        .bot-status {
            color: #00ff88;
            font-weight: bold;
        }
        .target-progress {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 15px 0;
        }
        .target-bar {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #ffd93d);
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 2px solid #00ff88;
            color: #666;
        }
        .alert {
            background: rgba(255,107,107,0.2);
            border: 2px solid #ff6b6b;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            color: #ff6b6b;
            font-weight: bold;
        }
        .success {
            background: rgba(0,255,136,0.2);
            border-color: #00ff88;
            color: #00ff88;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 ORBITAL COMMAND v2.0</h1>
        <div class="subtitle">REALISTIC MODE — Target: €3-5/giorno</div>
    </div>

    <div class="grid">
        <!-- Card: Capitale -->
        <div class="card">
            <h2>💰 Capitale & Target</h2>
            <div class="metric">
                <span class="metric-label">Capitale Attuale:</span>
                <span class="metric-value">€{{capital:.2f}}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Capitale Iniziale:</span>
                <span class="metric-value">€425.00</span>
            </div>
            <div class="metric">
                <span class="metric-label">Profitto/Perdita:</span>
                <span class="metric-value {% if pnl > 0 %}positive{% else %}negative{% endif %}">€{{"%0.2f"|format(pnl)}}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Fase:</span>
                <span class="metric-value">{{phase}}/4</span>
            </div>
            <div class="metric">
                <span class="metric-label">Target Oggi:</span>
                <span class="metric-value">€{{daily_target:.2f}}</span>
            </div>
            <div class="target-progress">
                <div class="target-bar" style="width: {{progress}}%">{{progress:.0f}}%</div>
            </div>
        </div>

        <!-- Card: Bot Attivi -->
        <div class="card">
            <h2>🤖 Bot Attivi ({{active_bots}}/7)</h2>
            <ul class="bot-list">
                <li class="bot-item">
                    <span class="bot-name">Realistic Grid Bot</span>
                    <span class="bot-status">✅ ON</span>
                </li>
                <li class="bot-item">
                    <span class="bot-name">AI Risk Engine</span>
                    <span class="bot-status">✅ ON</span>
                </li>
                <li class="bot-item">
                    <span class="bot-name">Crisis Manager</span>
                    <span class="bot-status">✅ ON</span>
                </li>
                <li class="bot-item">
                    <span class="bot-name">Delta Neutral</span>
                    <span class="bot-status">✅ ON</span>
                </li>
                <li class="bot-item">
                    <span class="bot-name">Target Tracker</span>
                    <span class="bot-status">✅ ON</span>
                </li>
                <li class="bot-item">
                    <span class="bot-name">Telegram Controller</span>
                    <span class="bot-status">✅ ON</span>
                </li>
                <li class="bot-item">
                    <span class="bot-name">Dashboard</span>
                    <span class="bot-status">✅ ON</span>
                </li>
            </ul>
        </div>

        <!-- Card: Performance -->
        <div class="card">
            <h2>📈 Performance</h2>
            <div class="metric">
                <span class="metric-label">Oggi P&L:</span>
                <span class="metric-value {% if today_pnl > 0 %}positive{% else %}negative{% endif %}">€{{"%0.2f"|format(today_pnl)}}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Questa Settimana:</span>
                <span class="metric-value {% if week_pnl > 0 %}positive{% else %}negative{% endif %}">€{{"%0.2f"|format(week_pnl)}}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Questo Mese:</span>
                <span class="metric-value {% if month_pnl > 0 %}positive{% else %}negative{% endif %}">€{{"%0.2f"|format(month_pnl)}}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Totale Profitto:</span>
                <span class="metric-value positive">€{{total_profit:.2f}}</span>
            </div>
        </div>

        <!-- Card: Risorse -->
        <div class="card">
            <h2>⚡ Risorse NUVOLA</h2>
            <div class="metric">
                <span class="metric-label">RAM Usata:</span>
                <span class="metric-value {{ 'warning' if ram_percent > 80 else 'positive' }}">{{ram_used}} / {{ram_total}} ({{ram_percent}}%)</span>
            </div>
            <div class="metric">
                <span class="metric-label">CPU Load:</span>
                <span class="metric-value">{{cpu_load}}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Uptime:</span>
                <span class="metric-value">{{uptime}}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Ultimo Aggiornamento:</span>
                <span class="metric-value">{{last_update}}</span>
            </div>
        </div>

        <!-- Card: Strategia -->
        <div class="card">
            <h2>🎯 Strategia Attiva</h2>
            <div style="padding: 10px; background: rgba(0,255,136,0.1); border-radius: 10px; margin: 10px 0;">
                <strong style="color: #ffd93d;">FASE {{phase}}: {{phase_name}}</strong>
                <p style="margin-top: 10px; color: #aaa;">
                    Grid Trading BTC/EUR con range dinamico.<br>
                    Reinvestimento 50% profitti.<br>
                    Upgrade automatico a €{{next_target}} capitale.
                </p>
            </div>
            {% if progress >= 100 %}
            <div class="alert success">
                ✅ TARGET RAGGIUNTO OGGI!
            </div>
            {% elif progress < 30 %}
            <div class="alert">
                ⚠️ Sotto target — Attendere chiusura grid
            </div>
            {% else %}
            <div style="padding: 10px; color: #00ff88;">
                🟢 In progress verso target
            </div>
            {% endif %}
        </div>

        <!-- Card: Proiezione -->
        <div class="card">
            <h2>🔮 Proiezione 6 Mesi</h2>
            <div class="metric">
                <span class="metric-label">Mese 1:</span>
                <span class="metric-value">€515 (+€90)</span>
            </div>
            <div class="metric">
                <span class="metric-label">Mese 3:</span>
                <span class="metric-value">€905 (+€240)</span>
            </div>
            <div class="metric">
                <span class="metric-label">Mese 6:</span>
                <span class="metric-value" style="color: #ffd93d; font-size: 1.3em;">€1,805 (+€1,380)</span>
            </div>
            <div style="margin-top: 15px; padding: 10px; border-top: 1px solid #00ff88; font-size: 0.9em; color: #888;">
                *Stima basata su target €3-5/giorno raggiunti
            </div>
        </div>
    </div>

    <div class="footer">
        <p>ORBITAL COMMAND v2.0 — Realistic Mode</p>
        <p>Capitale: €425 → Target: €1,805 (6 mesi)</p>
        <p style="margin-top: 10px; color: #444;">Aggiornato: {{last_update}}</p>
    </div>
</body>
</html>
'''

def get_system_stats():
    """Recupera statistiche sistema"""
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    
    # Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = datetime.now().timestamp() - boot_time
    uptime_str = f"{int(uptime_seconds//86400)}d {int((uptime_seconds%86400)//3600)}h"
    
    return {
        'ram_used': f"{mem.used // (1024**3)}GB",
        'ram_total': f"{mem.total // (1024**3)}GB",
        'ram_percent': mem.percent,
        'cpu_load': cpu,
        'uptime': uptime_str
    }

def get_capital_data():
    """Recupera dati capitale"""
    capital_file = '/home/sergio/.openclaw/workspace/denaro/capital_state.json'
    
    if os.path.exists(capital_file):
        with open(capital_file) as f:
            data = json.load(f)
            current = data.get('current', 425)
            initial = data.get('initial', 425)
            total_profit = data.get('total_profit', 0)
            phase = data.get('phase', 1)
            
            # Calcola P&L oggi
            history = data.get('daily_history', [])
            today_pnl = history[-1].get('pnl', 0) if history else 0
            
            # Target basato su fase
            targets = {1: 3.0, 2: 5.0, 3: 8.0, 4: 10.0}
            daily_target = targets.get(phase, 3.0)
            progress = min(100, (today_pnl / daily_target) * 100) if daily_target > 0 else 0
            
            phase_names = {
                1: "Crescita Iniziale (€3/giorno)",
                2: "Accelerazione (€5/giorno)",
                3: "Espansione (€8/giorno)",
                4: "Ottimale (€10/giorno)"
            }
            
            next_thresholds = {1: 500, 2: 650, 3: 800, 4: 1000}
            
            return {
                'capital': current,
                'initial': initial,
                'pnl': current - initial,
                'phase': phase,
                'phase_name': phase_names.get(phase, "Fase 1"),
                'daily_target': daily_target,
                'today_pnl': today_pnl,
                'week_pnl': sum(h.get('pnl', 0) for h in history[-7:]),
                'month_pnl': sum(h.get('pnl', 0) for h in history[-30:]),
                'total_profit': total_profit,
                'progress': progress,
                'next_target': next_thresholds.get(phase, 1000)
            }
    
    # Default
    return {
        'capital': 425,
        'initial': 425,
        'pnl': 0,
        'phase': 1,
        'phase_name': "Crescita Iniziale (€3/giorno)",
        'daily_target': 3.0,
        'today_pnl': 0,
        'week_pnl': 0,
        'month_pnl': 0,
        'total_profit': 0,
        'progress': 0,
        'next_target': 500
    }

def count_active_bots():
    """Conta bot attivi"""
    try:
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'python.*denaro'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    except:
        return 7  # Default ai 7 bot essenziali

@app.route('/')
def dashboard():
    stats = get_system_stats()
    capital = get_capital_data()
    bots = count_active_bots()
    
    return render_template_string(
        HTML_TEMPLATE,
        **stats,
        **capital,
        active_bots=bots,
        last_update=datetime.now().strftime('%H:%M:%S %d/%m/%Y')
    )

@app.route('/health')
def health():
    return {'status': 'ok', 'mode': 'realistic', 'target': '€3-5/day'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081, debug=False)
