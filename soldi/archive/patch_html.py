with open("dashboard/index.html", "r") as f:
    html = f.read()

# Find stat boxes
mexc_card = """
            <div class="panel stat-box profit">
                <div class="stat-val green" id="stat-mexc">0.00$</div>
                <div class="stat-label">MEXC LABORATORY [NANO]</div>
            </div>
"""
# insert before the closing div of the stat boxes
html = html.replace('<div class="panel stat-box vault">', mexc_card + '\n            <div class="panel stat-box vault">')

# find JS that updates stats
js_update = """
                document.getElementById('stat-vault').innerText = data.vault + '€';
                if(data.mexc_liquid) {
                    document.getElementById('stat-mexc').innerText = data.mexc_liquid + '$';
                }
"""
html = html.replace("document.getElementById('stat-vault').innerText = data.vault + '€';", js_update)

with open("dashboard/index.html", "w") as f:
    f.write(html)
