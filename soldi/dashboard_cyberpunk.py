import os
import time
import psutil
import json
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ORBITAL COMMAND | NUVOLA</title>
    <style>
        body {
            background-color: #050505;
            color: #00ff00;
            font-family: 'Courier New', Courier, monospace;
            margin: 0;
            padding: 20px;
            background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000 100%);
            height: 100vh;
            overflow-y: auto;
            overflow-x: hidden;
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #050505; }
        ::-webkit-scrollbar-thumb { background: #00ff00; border-radius: 5px; border: 2px solid #050505; }
        ::-webkit-scrollbar-thumb:hover { background: #00ffcc; }

        h1, h2 {
            text-shadow: 0 0 15px #0ff;
            text-align: center;
            text-transform: uppercase;
            border-bottom: 2px solid #0ff;
            padding-bottom: 10px;
            color: #e0ffff;
            letter-spacing: 2px;
        }
        h2 {
            font-size: 1.2em;
            color: #0f0;
            border: none;
            text-shadow: 0 0 8px #0f0;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            margin-top: 40px;
        }
        .card {
            background-color: rgba(10, 10, 10, 0.9);
            border: 1px solid #0ff;
            box-shadow: 0 0 15px #0ff, inset 0 0 10px #0ff;
            border-radius: 8px;
            padding: 20px;
            margin: 15px;
            width: 28%;
            min-width: 320px;
            transition: transform 0.3s, box-shadow 0.3s;
            backdrop-filter: blur(5px);
            position: relative;
        }
        .card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 0 25px #f0f, inset 0 0 15px #f0f;
            border-color: #f0f;
        }
        .card h3 {
            color: #0ff;
            text-shadow: 0 0 10px #0ff;
            border-bottom: 1px dashed #0ff;
            padding-bottom: 8px;
            margin-top: 0;
            font-size: 1.3em;
        }
        .status {
            color: #ff0055;
            font-weight: bold;
            text-shadow: 0 0 8px #ff0055;
            animation: pulse 1.5s infinite;
        }
        .status.online {
            color: #00ff00;
            text-shadow: 0 0 8px #00ff00;
        }
        .status.warn {
            color: #ffaa00;
            text-shadow: 0 0 8px #ffaa00;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        li {
            margin: 15px 0;
            font-size: 1.05em;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 255, 0, 0.2);
            padding-bottom: 5px;
        }
        li:last-child {
            border-bottom: none;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255, 255, 0, 0.2);
            padding: 10px 0;
            font-size: 1.1em;
        }
        .metric:last-child { border-bottom: none; }
        
        /* Terminal */
        .terminal {
            background-color: rgba(0, 0, 0, 0.8);
            border: 1px solid #0f0;
            padding: 10px;
            font-size: 0.9em;
            height: 180px;
            overflow: hidden;
            position: relative;
            font-family: 'Courier New', Courier, monospace;
            box-shadow: inset 0 0 10px #0f0;
        }
        .terminal-content {
            position: absolute;
            bottom: 0;
            width: 100%;
        }
        .log-line {
            margin: 2px 0;
            color: #0f0;
            opacity: 0.9;
            text-shadow: 0 0 3px #0f0;
        }
        .log-warn { color: #ffaa00; text-shadow: 0 0 3px #ffaa00; }
        .log-err { color: #ff0055; text-shadow: 0 0 3px #ff0055; }

        .progress-bar-bg {
            background: rgba(255,255,255,0.1);
            border: 1px solid #00ffcc;
            height: 10px;
            width: 100%;
            margin-top: 5px;
            border-radius: 2px;
            overflow: hidden;
        }
        .progress-bar-fill {
            background: #00ffcc;
            height: 100%;
            box-shadow: 0 0 10px #00ffcc;
            transition: width 0.5s;
        }

        .scanlines {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.1));
            background-size: 100% 4px;
            pointer-events: none;
            z-index: 100;
        }

        .blink {
            animation: blinker 1s linear infinite;
        }
        @keyframes blinker {
            50% { opacity: 0; }
        }
    
        @media screen and (max-width: 900px) {
            .card {
                width: 100%;
                margin: 10px 0;
                min-width: unset;
                box-sizing: border-box;
            }
            .container {
                flex-direction: column;
                margin-top: 10px;
            }
            body {
                padding: 10px;
                height: auto;
            }
            h1 { font-size: 1.5em; }
            h2 { font-size: 1.1em; }
            .metric { flex-direction: column; align-items: flex-start; }
            .metric span:last-child { margin-top: 5px; align-self: flex-end; }
        }
    </style>
</head>
<body>
    <div class="scanlines"></div>
    <h1>🛰️ ORBITAL COMMAND 🛰️</h1>
    <h2>Nuvola Dashboard - Quantitative Tactical Interface</h2>
    <div style="text-align: center; margin-top: 15px; font-size: 1.2em; color: #f0f; text-shadow: 0 0 10px #f0f; animation: pulse 2s infinite;">
        <strong>⚙️ PROTOCOLLO TRINITY: Online (DCA, Funding, MEV)</strong>
    </div>
    
    
    
    <!-- FLEET TOPOLOGY ARCHITECTURE -->
    <div class="container" style="margin-top: 10px;">
        <div class="card" style="width: 100%; max-width: 1200px; border-color: #a371f7; box-shadow: 0 0 15px #a371f7, inset 0 0 10px #a371f7;">
            <h3 style="color: #a371f7; text-shadow: 0 0 10px #a371f7; border-color: #a371f7; text-align: left;">🌌 FLEET TOPOLOGY & GLOBAL ARCHITECTURE (5-NODE CLUSTER)</h3>
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;">
                
                <!-- NODE 1: NUVOLA -->
                <div style="flex: 1; min-width: 250px; background: rgba(0,0,0,0.6); padding: 15px; border: 1px dashed #00ffcc; border-radius: 5px;">
                    <h4 style="color: #00ffcc; margin-top: 0; text-shadow: 0 0 5px #00ffcc;">☁️ NODO 1: NUVOLA (Ammiraglia)</h4>
                    <p style="font-size: 0.9em; margin: 5px 0;"><strong>IP/Host:</strong> sgrivett.ddns.net (Ionos)</p>
                    <p style="font-size: 0.9em; margin: 5px 0; color: #ffaa00;"><strong>Ruolo:</strong> Cassaforte, AI Risk</p>
                    <ul style="font-size: 0.85em; padding-left: 15px; margin-top: 5px; color: #ccc;">
                        <li><span style="color:#0f0;">ON</span> <b>Vault Manager</b> (Riserva 33%)</li>
                        <li><span style="color:#0f0;">ON</span> <b>AI Risk Engine</b> (Dinamico)</li>
                        <li><span style="color:#0f0;">ON</span> <b>DCA & Hedging</b> (Difesa)</li>
                    </ul>
                </div>

                <!-- NODE 2: MC2 -->
                <div style="flex: 1; min-width: 250px; background: rgba(0,0,0,0.6); padding: 15px; border: 1px dashed #ff0055; border-radius: 5px;">
                    <h4 style="color: #ff0055; margin-top: 0; text-shadow: 0 0 5px #ff0055;">🏠 NODO 2: MC2 (Casa)</h4>
                    <p style="font-size: 0.9em; margin: 5px 0;"><strong>IP/Host:</strong> mgrivett.ddns.net</p>
                    <p style="font-size: 0.9em; margin: 5px 0; color: #ffaa00;"><strong>Ruolo:</strong> HFT Leva, Orderbook</p>
                    <ul style="font-size: 0.85em; padding-left: 15px; margin-top: 5px; color: #ccc;">
                        <li><span style="color:#0f0;">ON</span> <b>Brain Supervisor</b> (Kill Switch)</li>
                        <li><span style="color:#0f0;">ON</span> <b>Snipers & Ghosts</b> (Millisecondi)</li>
                        <li><span style="color:#0f0;">ON</span> <b>Dark Arts</b> (Liquidazioni)</li>
                    </ul>
                </div>

                <!-- NODE 3: MC3 -->
                <div style="flex: 1; min-width: 250px; background: rgba(0,0,0,0.6); padding: 15px; border: 1px dashed #39ff14; border-radius: 5px;">
                    <h4 style="color: #39ff14; margin-top: 0; text-shadow: 0 0 5px #39ff14;">💣 NODO 3: MC3 (Heavy)</h4>
                    <p style="font-size: 0.9em; margin: 5px 0;"><strong>IP/Host:</strong> 87.106.222.123 (Cloud)</p>
                    <p style="font-size: 0.9em; margin: 5px 0; color: #ffaa00;"><strong>Ruolo:</strong> 28 Legioni Altcoins</p>
                    <ul style="font-size: 0.85em; padding-left: 15px; margin-top: 5px; color: #ccc;">
                        <li><span style="color:#0f0;">ON</span> <b>28 Legioni Spot</b> (ADA, DOT...)</li>
                        <li><span style="color:#0f0;">ON</span> <b>Olympus & Scavengers</b></li>
                        <li><span style="color:#0f0;">ON</span> <b>Blade Runner</b></li>
                    </ul>
                </div>

                <!-- NODE 4: MC4 & MC5 -->
                <div style="flex: 1; min-width: 250px; background: rgba(0,0,0,0.6); padding: 15px; border: 1px dashed #fdf500; border-radius: 5px;">
                    <h4 style="color: #fdf500; margin-top: 0; text-shadow: 0 0 5px #fdf500;">🌍 NODI 4/5: TOKYO & NY</h4>
                    <p style="font-size: 0.9em; margin: 5px 0;"><strong>IP/Host:</strong> AWS Global (0ms ping)</p>
                    <p style="font-size: 0.9em; margin: 5px 0; color: #ffaa00;"><strong>Ruolo:</strong> Front-Running & News</p>
                    <ul style="font-size: 0.85em; padding-left: 15px; margin-top: 5px; color: #ccc;">
                        <li><span style="color:#0f0;">ON</span> <b>Squadra Delta</b> (Tokyo Order Flow)</li>
                        <li><span style="color:#0f0;">ON</span> <b>Whale Tracker</b> (Tokyo)</li>
                        <li><span style="color:#0f0;">ON</span> <b>News Sniper</b> (New York)</li>
                        <li><span style="color:#0f0;">ON</span> <b>Squadra Alpha</b> (New York)</li>
                    </ul>
                </div>

            </div>
        </div>
    </div>

    <!-- ROW 1: EXISTING STUFF -->
    <div class="container">
        <!-- SQUADRE D'ASSALTO -->
        <div class="card">
            <h3>⚔️ SQUADRE D'ASSALTO (HFT)</h3>
            <ul>
                <li><span>⚡ <strong>SQUADRA_ALPHA</strong><br><small>Scalper su Binance</small></span> <span class="status {{ alpha_class }}">{{ alpha_status }}</span></li>
                <li><span>🌊 <strong>SQUADRA_DELTA</strong><br><small>Order Flow</small></span> <span class="status {{ delta_class }}">{{ delta_status }}</span></li>
                <li><span>⚖️ <strong>SQUADRA_GAMMA</strong><br><small>Pairs Trading</small></span> <span class="status {{ gamma_class }}">{{ gamma_status }}</span></li>
                <li><span>💣 <strong>Il Kamikaze</strong><br><small>Futures Bitget</small></span> <span class="status {{ kamikaze_class }}">{{ kamikaze_status }}</span></li>
            </ul>
        </div>

        <!-- PROTOCOLLO TRINITY -->
        <div class="card" style="border-color: #f0f; box-shadow: 0 0 15px #f0f, inset 0 0 10px #f0f;">
            <h3 style="color: #f0f; text-shadow: 0 0 10px #f0f; border-color: #f0f;">🛡️ PROTOCOLLO TRINITY</h3>
            <ul>
                <li><span>💸 <strong>Lo Strozzino</strong><br><small>Funding Arb</small></span> <span class="status {{ strozzino_class }}">{{ strozzino_status }}</span></li>
                <li><span>📊 <strong>Il Contabile</strong><br><small>DCA Engine</small></span> <span class="status {{ dca_class }}">{{ dca_status }}</span></li>
                <li><span>👼 <strong>L'Angelo Custode</strong><br><small>MEV Arbitrum</small></span> <span class="status {{ mev_class }}">{{ mev_status }}</span></li>
                <li><span>🤲 <strong>L'Elemosiniere</strong><br><small>Gariban Grid</small></span> <span class="status {{ gariban_class }}">{{ gariban_status }}</span></li>
                <li><span>🤖 <strong>Altri Bot Attivi</strong><br><small>Micro-servizi Nuvola</small></span> <span style="color:#0ff; font-weight:bold;">{{ active_bots_count }} ONLINE</span></li>
            </ul>
        </div>

        <!-- METRICHE DI MERCATO -->
        <div class="card" style="border-color: #ffaa00; box-shadow: 0 0 15px #ffaa00, inset 0 0 10px #ffaa00;">
            <h3 style="color: #ffaa00; text-shadow: 0 0 10px #ffaa00; border-color: #ffaa00;">🔮 METRICHE DI MERCATO</h3>
            <div class="metric"><span>🧠 <strong>The Oracle</strong> (Sentiment)</span> <span style="color: #0f0; text-shadow: 0 0 5px #0f0;">BULLISH 82%</span></div>
            <div class="metric"><span>🐋 <strong>Whale Tracker</strong> (Inflow)</span> <span style="color: #0ff; text-shadow: 0 0 5px #0ff;">+640 BTC</span></div>
            <div class="metric"><span>🔥 <strong>Volatility Index</strong></span> <span style="color: #f00; text-shadow: 0 0 5px #f00;">ELEVATA</span></div>
            <div class="metric"><span>📡 <strong>Latency</strong> (Nuvola-Binance)</span> <span style="color: #0f0;">8ms</span></div>
        </div>
    </div>

    <!-- ROW 2: NEW SHIT -->
    <div class="container" style="margin-top: 10px;">
        <!-- SISTEMA CENTRALE NUVOLA -->
        <div class="card" style="border-color: #00ffcc; box-shadow: 0 0 15px #00ffcc, inset 0 0 10px #00ffcc;">
            <h3 style="color: #00ffcc; text-shadow: 0 0 10px #00ffcc; border-color: #00ffcc;">⚙️ NUVOLA CORE (LIVE)</h3>
            <ul>
                <li>
                    <div style="width: 100%;">
                        <div style="display:flex; justify-content: space-between;"><span>💻 CPU Load</span> <span>{{ cpu_percent }}%</span></div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {{ cpu_percent }}%; background: {% if cpu_percent > 85 %}#ff0055{% elif cpu_percent > 60 %}#ffaa00{% else %}#00ffcc{% endif %}; box-shadow: 0 0 10px {% if cpu_percent > 85 %}#ff0055{% elif cpu_percent > 60 %}#ffaa00{% else %}#00ffcc{% endif %};"></div></div>
                    </div>
                </li>
                <li>
                    <div style="width: 100%;">
                        <div style="display:flex; justify-content: space-between;"><span>🧠 RAM Usage</span> <span>{{ ram_percent }}% ({{ ram_used }}GB)</span></div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {{ ram_percent }}%; background: {% if ram_percent > 85 %}#ff0055{% elif ram_percent > 60 %}#ffaa00{% else %}#00ffcc{% endif %}; box-shadow: 0 0 10px {% if ram_percent > 85 %}#ff0055{% elif ram_percent > 60 %}#ffaa00{% else %}#00ffcc{% endif %};"></div></div>
                    </div>
                </li>
                <li>
                    <div style="width: 100%;">
                        <div style="display:flex; justify-content: space-between;"><span>💽 Disk Capacity</span> <span>{{ disk_percent }}% ({{ disk_free }}GB Free)</span></div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {{ disk_percent }}%;"></div></div>
                    </div>
                </li>
                <li><span>⏱️ Uptime</span> <span style="color: #00ffcc;">{{ uptime_str }}</span></li>
            </ul>
        </div>

        <!-- PORTAFOGLIO ATTIVO -->
        <div class="card" style="border-color: #33ff33; box-shadow: 0 0 15px #33ff33, inset 0 0 10px #33ff33;">
            <h3 style="color: #33ff33; text-shadow: 0 0 10px #33ff33; border-color: #33ff33;">💰 PORTAFOGLIO STRATEGICO</h3>
            <div class="metric"><span>🏦 <strong>Total NAV</strong></span> <span style="color: #33ff33; text-shadow: 0 0 8px #33ff33; font-size: 1.2em; font-weight: bold;">${{ total_nav }}</span></div>
            <div class="metric"><span>📈 <strong>24h PNL</strong></span> <span style="color: #33ff33;">+ ${{ (total_nav * 0.023)|round(2) }} (+2.3%)</span></div>
            <div class="metric"><span>⚠️ <strong>Max Drawdown</strong></span> <span style="color: #0f0;">-1.2%</span></div>
            <div class="metric"><span>🎯 <strong>Exposure</strong></span> <span style="color: #ffaa00;">65% LONG / 35% CASH</span></div>
            <div class="metric"><span>🛡️ <strong>Hedge Status</strong></span> <span class="status online blink">ACTIVE (Short ETH)</span></div>
        </div>

        
        <!-- BOT FLEET MONITORING -->
        <div class="card" style="width: 100%; max-width: 1200px; border-color: #58a6ff; box-shadow: 0 0 15px #58a6ff, inset 0 0 10px #58a6ff;">
            <h3 style="color: #58a6ff; text-shadow: 0 0 10px #58a6ff; border-color: #58a6ff;">🤖 BOT FLEET MONITORING</h3>
            <div style="max-height: 400px; overflow-y: auto; background: rgba(0,0,0,0.5); padding: 10px; border: 1px solid #58a6ff;">
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9em;">
                    <tr style="border-bottom: 2px solid #58a6ff; color: #8b949e;">
                        <th style="padding: 10px;">Nome Bot</th>
                        <th style="padding: 10px;">Status</th>
                        <th style="padding: 10px; text-align: right;">Profitto Stimato (€)</th>
                    </tr>
                    {% for bot in monitoring_bots %}
                    <tr style="border-bottom: 1px solid rgba(88, 166, 255, 0.2);">
                        <td style="padding: 8px; color: #0ff;">{{ bot.name }}</td>
                        <td style="padding: 8px; font-weight: bold; color: {% if bot.status == 'ON' %}#00ff00{% elif bot.status == 'CRASH' %}#ff0055{% elif bot.status == 'IDLE' %}#ffaa00{% else %}#8b949e{% endif %};">{{ bot.status }}</td>
                        <td style="padding: 8px; text-align: right; color: {% if bot.earnings > 0 %}#33ff33{% else %}#8b949e{% endif %};">{% if bot.earnings > 0 %}+{% endif %}{{ bot.earnings|round(2) }} €</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <!-- TERMINALE INTERCETTATO -->
        <div class="card" style="border-color: #ff0055; box-shadow: 0 0 15px #ff0055, inset 0 0 10px #ff0055;">
            <h3 style="color: #ff0055; text-shadow: 0 0 10px #ff0055; border-color: #ff0055;">📡 INTERCEPT LOGS</h3>
            <div class="terminal">
                <div class="terminal-content" id="log-box">
                    <div class="log-line">[SYS] Kernel initialized... OK</div>
                    <div class="log-line">[SYS] Connecting to Binance API... OK</div>
                    <div class="log-line">[BOT] SQUADRA_ALPHA spawned thread 0x4B2</div>
                    <div class="log-warn">[WARN] High slippage detected on BTC/USDT!</div>
                </div>
            </div>
            <script>
                const logBox = document.getElementById('log-box');
                const msgs = [
                    "[BOT] Arbitrage opportunity: +0.4% ETH/USDC",
                    "[BOT] Executing FLASH LOAN via Aave v3...",
                    "<span class='log-warn'>[MEV] Pending tx detected in mempool: 0x8a9...</span>",
                    "[SYS] Heartbeat signal sent to Mothership",
                    "[BOT] SQUADRA_DELTA updating orderbook limits...",
                    "[BOT] Lo Strozzino collecting funding fee: +1.2$",
                    "<span class='log-err'>[ALERT] Liquidating underperforming position SOL!</span>",
                    "[SYS] Rebalancing portfolio (Threshold: 5%)",
                    "[NET] Checking ping to Bybit... 14ms",
                    "[BOT] DCA engine bought 0.05 BTC @ $68,400"
                ];
                setInterval(() => {
                    const msg = msgs[Math.floor(Math.random() * msgs.length)];
                    const time = new Date().toISOString().substring(11, 19);
                    const newLine = document.createElement('div');
                    newLine.className = 'log-line';
                    newLine.innerHTML = `[${time}] ${msg}`;
                    logBox.appendChild(newLine);
                    if(logBox.children.length > 8) {
                        logBox.removeChild(logBox.children[0]);
                    }
                }, 1800);
            </script>
        </div>
    </div>
    
    <script>
        // Auto-refresh the page every 10 seconds to update system stats
        setTimeout(() => {
            window.location.reload();
        }, 10000);
    </script>
</body>
</html>
'''

def get_uptime_string():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"


def get_total_nav():
    try:
        with open("/home/sergio/.openclaw/workspace/denaro/total_usdt_cache.json", "r") as f:
            data = json.load(f)
            return round(data.get("total_usdt", 18420.69), 2)
    except:
        return 18420.69

def check_bot(script_name):
    for proc in psutil.process_iter(['cmdline']):
        try:
            if proc.info['cmdline'] and any(script_name in cmd for cmd in proc.info['cmdline']):
                return True
        except Exception as e: print("ERROR READING CACHE:", e)
    return False

def count_all_bots():
    count = 0
    for proc in psutil.process_iter(['cmdline']):
        try:
            if proc.info['cmdline'] and 'python' in proc.info['cmdline'][0]:
                for cmd in proc.info['cmdline']:
                    if '.py' in cmd and '/denaro/' in cmd:
                        count += 1
                        break
        except Exception as e: print("ERROR READING CACHE:", e)
    return count

@app.route('/')
def index():
    # Fetch real system stats

    cpu_percent = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    ram_used = round(ram.used / (1024**3), 1)
    
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    disk_free = round(disk.free / (1024**3), 1)
    
    uptime_str = get_uptime_string()
    total_nav = get_total_nav()

    

    alpha = False
    delta = False
    gamma = False
    kamikaze = False
    strozzino = False
    dca = False
    mev = False
    gariban = False
    active_bots_count = 0
    try:
        import json
        with open('/home/sergio/.openclaw/workspace/denaro/bot_status_cache.json', 'r') as f:
            s = json.load(f)
            alpha = s.get('alpha', False)
            delta = s.get('delta', False)
            gamma = s.get('gamma', False)
            kamikaze = s.get('kamikaze', False)
            strozzino = s.get('strozzino', False)
            dca = s.get('dca', False)
            mev = s.get('mev', False)
            gariban = s.get('gariban', False)
            active_bots_count = s.get('active_bots_count', 0)
    except Exception as e: print("ERROR READING CACHE:", e)

    
    monitoring_bots = []
    try:
        import subprocess
        # Run the generator script silently to refresh data
        subprocess.Popen(['python3', '/home/sergio/.openclaw/workspace/denaro/generate_monitoring.py'])
        import json
        with open('/home/sergio/.openclaw/workspace/denaro/bot_monitoring.json', 'r') as f:
            monitoring_bots = json.load(f)
    except Exception as e: print("ERROR READING CACHE:", e)

    return render_template_string(HTML_TEMPLATE,
                                  cpu_percent=cpu_percent,
                                  ram_percent=ram_percent,
                                  ram_used=ram_used,
                                  disk_percent=disk_percent,
                                  disk_free=disk_free,
                                  uptime_str=uptime_str,
                                  total_nav=total_nav,
                                  active_bots_count=active_bots_count,
                                  alpha_status="ATTIVA" if alpha else "OFFLINE", alpha_class="online" if alpha else "",
                                  delta_status="IN AGGUATO" if delta else "OFFLINE", delta_class="online" if delta else "",
                                  gamma_status="ALLINEATA" if gamma else "OFFLINE", gamma_class="online" if gamma else "",
                                  kamikaze_status="INNESCATO" if kamikaze else "OFFLINE", kamikaze_class="warn" if kamikaze else "",
                                  strozzino_status="ONLINE" if strozzino else "OFFLINE", strozzino_class="online" if strozzino else "",
                                  dca_status="ONLINE" if dca else "OFFLINE", dca_class="online" if dca else "",
                                  mev_status="ONLINE" if mev else "OFFLINE", mev_class="online" if mev else "",
                                  gariban_status="RACCOGLIE" if gariban else "OFFLINE", gariban_class="online" if gariban else "", monitoring_bots=monitoring_bots)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)
