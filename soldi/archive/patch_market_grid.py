import re

with open("dashboard/dashboard_server.py", "r") as f:
    code = f.read()

# Add market.json endpoint
market_json_handler = """
        elif self.path == '/market.json' or self.path.startswith('/market.json?'):
            try:
                import ccxt
                import os
                from dotenv import load_dotenv
                load_dotenv(os.path.join(BASE_DIR, '.env.mexc'))
                api_key = os.getenv('MEXC_API_KEY')
                mexc = ccxt.mexc({'apiKey': api_key, 'secret': os.getenv('MEXC_API_SECRET')})
                tickers = mexc.fetch_tickers(['SOL/USDT', 'DOGE/USDT', 'PEPE/USDT', 'XRP/USDT'])
                market_data = []
                for s, t in tickers.items():
                    market_data.append({
                        "symbol": s,
                        "price": t.get('last', 0),
                        "change": t.get('percentage', 0)
                    })
                data = json.dumps(market_data)
            except Exception as e:
                data = json.dumps([])
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data.encode())
            return
"""
code = code.replace("elif self.path == '/syslogs.json'", market_json_handler + "\n        elif self.path == '/syslogs.json'")

with open("dashboard/dashboard_server.py", "w") as f:
    f.write(code)

with open("dashboard/index.html", "r") as f:
    html = f.read()

js_update = """
            // Aggiorna Market Grid
            fetch('market.json?t=' + Date.now())
                .then(r => r.json())
                .then(data => {
                    const grid = document.getElementById('market-grid');
                    if(data.length > 0) {
                        let html = '';
                        data.forEach(coin => {
                            const isUp = coin.change >= 0;
                            const colorClass = isUp ? 'up' : 'down';
                            const sign = isUp ? '+' : '';
                            html += `
                            <div class="crypto-card ${colorClass}" style="background: rgba(0,0,0,0.6); padding: 10px; border: 1px solid #333; border-bottom: 2px solid ${isUp ? '#39ff14' : '#ff003c'}; text-align: center;">
                                <div style="font-size: 14px; color: #fff;">${coin.symbol}</div>
                                <div style="font-size: 16px; color: var(--cyan); margin: 5px 0;">$${coin.price}</div>
                                <div style="font-size: 12px; color: ${isUp ? '#39ff14' : '#ff003c'};">${sign}${coin.change}%</div>
                            </div>`;
                        });
                        grid.innerHTML = html;
                    }
                }).catch(e => console.log('Market grid error', e));
"""
html = html.replace("setTimeout(updateDashboard, 5000);", js_update + "\n            setTimeout(updateDashboard, 5000);")

with open("dashboard/index.html", "w") as f:
    f.write(html)
