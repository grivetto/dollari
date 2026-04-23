# 🪐 ORBITAL COMMAND: FLEET TOPOLOGY

## 1. NUVOLA (Cloud Server)
- **Host Name:** nuvola
- **Type:** Cloud VPS
- **Initial Capital Base:** 722.00 €
- **Role:** Ammiraglia (Flagship). Gestisce il grosso del capitale (oltre 600€ attuali), la "Cassaforte", gli Arbitraggi Spaziali, i Flash Loan DeFi su Arbitrum, e l'Hedger Delta-Neutral per proteggere il portafoglio. Ospita i 50 micro-servizi principali e l'interfaccia Telegram (`@Sergiotrdxbot`).

## 2. MC2 (On-Premise Server)
- **Host Name:** mc2
- **IP Address:** 93.43.252.114 (Port: 2222)
- **Type:** On-Premise (Fisico, Intel N150, 16GB RAM, 4-Core)
- **Initial Capital Base:** 100.00 €
- **Role:** Cacciatore HFT Isolato. Lavora tramite la libreria asincrona ad alta frequenza (ccxt.async_support). Analizza l'orderbook in millisecondi su BTC, ETH, SOL e DOGE con Leva 5x. Chiude tutte le posizioni ogni notte alle 23:50 e preleva i profitti verso lo Spot ogni domenica alle 23:55 (Weekly Harvest). Espone la dashboard su https://mgrivett.ddns.net.
