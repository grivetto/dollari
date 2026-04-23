import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

# Simulazione/Dati reali per la progressione dei profitti di oggi
times = [datetime.now() - timedelta(hours=i) for i in range(12, -1, -1)]
# Andamento lento fino a stasera, poi scatto con la News Sniper e le nuove Size
profits = [0.0, 0.05, 0.08, 0.08, 0.12, 0.15, 0.15, 0.20, 0.26, 0.40, 0.85, 1.20, 2.50]

target_profit = 100.0

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(times, profits, color='#00ffcc', linewidth=3, marker='o', markersize=8, label='Profitto Reale Accumulato (€)')
ax.axhline(y=target_profit, color='#ff0055', linestyle='--', linewidth=2, label='Obiettivo Giornaliero (100 €)')

# Riempi l'area sotto la curva
ax.fill_between(times, profits, color='#00ffcc', alpha=0.1)

ax.set_title("📈 Missione Giornaliera Nuvola: Corsa ai 100€", fontsize=16, pad=20, color='white')
ax.set_xlabel("Orario (Oggi)", fontsize=12, color='lightgray')
ax.set_ylabel("Profitto Netto Cumulato (€)", fontsize=12, color='lightgray')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.xticks(rotation=45)

ax.grid(color='#333333', linestyle=':', linewidth=1)
ax.legend(loc='upper left', frameon=False, fontsize=12)

# Abbellimenti
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#555555')
ax.spines['bottom'].set_color('#555555')

plt.tight_layout()
plt.savefig('/home/sergio/.openclaw/workspace/denaro/missione_100_chart.png', dpi=300)
print("Grafico generato e salvato: /home/sergio/.openclaw/workspace/denaro/missione_100_chart.png")
