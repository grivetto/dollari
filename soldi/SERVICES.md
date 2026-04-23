# SERVICES.md - Elenco dei servizi e processi chiave

## Servizi di sistema (systemd)
- safe-fleet-boot.service – Avvio graduale dei bot con monitoraggio RAM+swap (soglia 85%).

## Processi principali (in esecuzione)
- fleet_guardian.py – Monitoraggio di RAM, swap e stato dei bot; riavvio automatico in caso di failure.
- fleet_reporter.py – Aggiornamento periodico delle statistiche di flotta e invio report su Telegram.
- telegram_bot_interactive.py – Bot Telegram per comandi e notifiche.
- dashboard_server.py – Server web che serve l'interfaccia (index.html, trades.html) e i file JSON (fleet_stats.json, trades_6h.json).

## Bot di trading (esempi chiave)
- sol_scalper.py – Scalping su SOL/EUR.
- btc_arbitrage_simple.py – Arbitraggio semplice su BTC.
- eth_market_maker.py – Market making su ETH/USDT.
- advanced_quant_bot.py – Strategia quantitativa basata su RSI e altri indicatori.
- liquidator_prime.py – Cattura di spike di liquidità.
- whale_order_tracker.py – Tracking di grandi ordini (whale).
- arbitrage_sentinel.py – Monitoraggio di opportunità di arbitraggio multi‑exchange.
- volatility_hunter.py – Trading basato su spike di volatilità.
- smart_grid_engine.py – Estrategia di grid trading.
- btc_volatility_sniper.py – Sniper su micro‑movimenti di BTC.
- sergio_wave_rider.py – Strategia di follow‑trend su onde di prezzo.
- aggressive_scalper.py – Scalping aggressivo su multiple coppie.
- bnb_mean_reversion.py – Mean reversion su BNB.
- sol_momentum_hunter.py – Momentum trading su SOL.
- eth_gas_price_trader.py – Trading basato sul prezzo del gas di Ethereum.
- hyper_mm_sol.py – Hyper market making su SOL.
- inverse_corr_bot.py – Trading su correlazioni inverse.
- architect_ai.py – AI per ottimizzazione di strategie.
- evolution_engine.py – Algoritmo evolutivo per generazione di strategie.
- war_machine.py – Bot di alta frequenza.
- omega_war_machine.py – Versione avanzata del war machine.
- bait_and_trap_engine.py – Strategia di bait‑and‑trap.
- rapid_cash_out.py – Chiusura rapida di posizioni per realizzare profitto.
- triad_sentinel_automa.py – Sistema di sentinella a triade.
- aggressive_scalper_aggregator.py – Aggregatore di segnali di aggressive scalper.
- multi_coin_rebalancer.py – Ribilanciamento del portafoglio multi‑coin.
- strategies/concept_gen_*.py – Strategie concettuali sperimentali (concept_gen_20.py … concept_gen_32.py).

## Servizi di supporto
- liquidity_harvester.py – Raccolta di liquidità dai order book.
- neural_pulse_v2.py – Rete neurale per predizione di breve termine.
- forced_profit_unit.py – Chiusura forzata di micro‑profitti.
- sigma_chaos_engine.py – Strategia caotica ad alta frequenza.
- sentiment_analyzer_bot.py – Analisi del sentiment da news/social.
- whale_pressure_scaler.py – Scalping basato sulla pressione delle whale.
- telegram_bot.py / telegram_bot_send*.py – Varianti di bot Telegram per notifiche specifiche.

Nota: l’elenco sopra non è esaustivo; per la lista completa vedere la directory `workspace/` e le sottocartelle `strategies/`.

Ultimo aggiornamento: $(date '+%Y-%m-%d %H:%M:%S')