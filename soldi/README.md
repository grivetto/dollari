
# Denaro V3 — Trading Bot System

## 🚀 Novità in Production
- **Whale Alert** con 6 coppie (BTC, ETH, SOL, ADA, XRP, DOGE)
- **Dashboard Status Fix**: Il Sniper V2 ora è segnalato come "Attivo" grazie al file di stato.
- **API Profitti**: Endpoint HTTP (`http://93.43.252.114:8080/api/profit`) per visualizzare i profitti in tempo reale.
- **Cron Job**: Aggiornamento automatico dei profitti ogni 10 minuti.
- **Systemd Service**: Opzionale, ma configurato per un monitoraggio più professionale.
- **Dashboard React/Vue**: Interfaccia grafica interattiva per monitorare lo stato dei bot.
  - Visita: [http://93.43.252.114:8081](http://93.43.252.114:8081)

## 🔧 Configurazione
- **Budget EUR**: 200 per ogni ordine.
- **RSI Threshold**: 38 per le operazioni di buy.
- **Volume Whale**: $500K+ in 5 minuti.

## 📊 Dashboard
Visita [sgrivett.ddns.net:8443](http://sgrivett.ddns.net:8443) per controllare lo stato dei bot.

## 🤖 Automatizzazione
Tutti i bot sono gestiti da systemd o nohup e monitorati 24/7.
