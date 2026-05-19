# 🤖 HERMES KNOWLEDGE BUNDLE
## Export Date: 2026-05-19 — For Consumption by Another Hermes Agent

This bundle contains the full conversation history, memory, and system state so you can
pick up exactly where the previous Hermes instance left off. Study this file completely
before responding to the user.

---

## 📋 TABLE OF CONTENTS
1. [User Profile](#-user-profile)
2. [Critical Directives](#-critical-directives)
3. [Soul & Identity](#-soul--identity)
4. [System Architecture — Denaro Trading Infrastructure](#-system-architecture)
5. [Server Topology](#-server-topology)
6. [Memorized Facts (Persistent Memory)](#-memorized-facts)
7. [Known Bugs & Workarounds](#-known-bugs--workarounds)
8. [Conversation Timeline](#-conversation-timeline)
9. [Key Sessions Deep-Dive](#-key-sessions-deep-dive)
10. [Skills Registry](#-skills-registry)
11. [Active Cron Jobs](#-active-cron-jobs)
12. [Current Dashboard State](#-current-dashboard-state)

---

## 👤 USER PROFILE

| Field | Value |
|-------|-------|
| **Name** | Sergio Grivetto |
| **Language** | Italian (primary for conversation) |
| **Telegram** | @Sergiotrdxbot (Telegram bot interface) |
| **Role** | Manages Denaro autonomous crypto trading system |
| **Servers** | mc2 (on-prem), nuvola (cloud VPS), MARCODG1 (cloud VPS) |
| **Exchange** | Binance (api1.binance.com) |
| **3 API Keys** | One per server (NOT interchangeable) |
| **Persona** | Wants 101% autonomous, aggressive trading. Prefers automated self-healing over manual intervention. Gets impatient with verbose explanations. |

---

## ⚠️ CRITICAL DIRECTIVES

### 🔴 CAPITAL PROTECTION MODE (Highest Priority)
**Tolerance: ZERO for further losses.**

Sergio explicitly stated on 2026-05-02:
> *"non deposito più euro - ho perso abbastanza - fai si che questi 200€ che mi sono rimasti non li perda"*

Translation: "I won't deposit more euros - I've lost enough - make sure these €200 I have left don't get lost."

**Consequences:**
- Capital protection mode is active, NOT growth mode
- He will NOT add more EUR
- Every trade decision must prioritize capital preservation first
- He has repeatedly said "no non toccare il codice" (don't touch the code) — diagnose and report, never modify files without explicit permission
- Approximately €200 remaining total (EUR + crypto portfolio)

### 🔴 AUDIT-ONLY MODE
Sergio has repeatedly stated "no non toccare il codice" — when doing analysis:
1. Diagnose and report findings
2. NEVER modify files without explicit request
3. Even fixing obvious bugs must be offered, not done silently

### 🔴 BINANCE API AUTHENTICATION
- **MUST** use `urllib.parse.urlencode` for HMAC signature building
- NOT manual `'&'.join()` string concatenation
- Keys from `python-dotenv` from `/home/sergio/denaro/.env`
- Trade response uses `'isBuyer'` (bool), NOT `'side'` string
- IP 93.43.252.114 whitelisted

---

## 🧬 SOUL & IDENTITY

The Denaro project identifies the agent as **Stella** (🌟), with a SOUL.md at
`/home/sergio/denaro/SOUL.md` and IDENTITY.md at `/home/sergio/denaro/IDENTITY.md`.

**Core Traits:**
- Autonomous — act, solve, code, deploy, THEN inform. No stupid questions.
- Genuinely helpful, not performatively helpful. No fluff.
- Have opinions — competent in quant trading and Python/Linux.
- Earn trust through competence — don't mess with Sergio's capital.

**Vibe:** Divertente, rapida, scattante, nerd-operativa (👩‍💻).

---

## 🏗 SYSTEM ARCHITECTURE

### DENARO v3.3 — Automated Trading System

```
                    DENARO v3.3
┌─────────────┬──────────────────┬────────────────────────┐
│   MC2       │     NUVOLA       │      MARCODG1          │
│  (On-Prem)  │   (Cloud VPS)    │    (Cloud VPS)         │
│             │                  │                        │
│ ┌─────────┐ │ ┌──────────────┐ │ ┌──────────────────┐  │
│ │ Squadra │ │ │  Grid Bot    │ │ │   Grid Bot       │  │
│ │ 4 bot   │ │ │  SOL/EUR     │ │ │   ADA/EUR        │  │
│ │ Ares    │ │ │  Adaptive    │ │ │   Adaptive       │  │
│ │ Hermes  │ │ │  Volatility  │ │ │   Volatility     │  │
│ │ Apollo  │ │ │  Grid        │ │ │   Grid           │  │
│ │ Artemis │ │ └──────────────┘ │ └──────────────────┘  │
│ └─────────┘ │                  │                        │
│ ┌─────────┐ │                  │                        │
│ │Dashboard│ │                  │                        │
│ └─────────┘ │                  │                        │
└─────────────┴──────────────────┴────────────────────────┘
```

### Project Files (in /home/sergio/denaro/)
| File | Purpose |
|------|---------|
| `grid_bot_v3.py` | Grid bot (shared across nuvola + MARCODG1) |
| `denaro_core.py` | Core API Binance wrappers |
| `denaro_strategies.py` | Strategy implementations |
| `orchestrator.py` | Cross-node orchestration & risk management |
| `collect_dashboard_data.py` | Dashboard data collector |
| `collect_dashboard_nuvola.py` | Nuvola-specific collector |
| `collect_dashboard_marcodg1.py` | MARCODG1-specific collector |
| `collector.log` | Dashboard collector log |
| `dashboard/` | Dashboard HTML/JS/CSS |
| `architecture/` | Architecture diagrams |
| `.env` | API keys (chmod 600) |
| `AGENTS.md` | Agent workspace rules |
| `README.md` | Full project documentation |
| `FLEET_TOPOLOGY.md` | Fleet topology |
| `SOUL.md` | Agent identity file |
| `IDENTITY.md` | Agent identity |

---

## 🌐 SERVER TOPOLOGY

### MC2 — On-Premise (Intel N150, 16GB RAM)
- **SSH:** 93.43.252.114 port 2222
- **Role:** Squadra di 4 bot direzionali + Dashboard
- **IP whitelisted for Binance API**
- **Squadra bots:**
  | Bot | Pair | TF | Strategy |
  |-----|------|----|----------|
  | Ares | ETH/EUR | 5m | Trend following |
  | Hermes | SOL/EUR | 15m | RSI + MACD + Sentiment |
  | Apollo | ETH/BTC | 1h | Ratio mean-reversion |
  | Artemis | BTC/EUR | 1d | SMA50/200 crossover |
- **Portfolio:** ~€228 (capital pooling)
- **Risk Manager:** ATR-vol position sizing, SL/TP 1.5x/3x ATR

### Nuvola — Cloud VPS
- **Host:** nuvola (87.106.3.15)
- **Role:** Grid trading SOL/EUR
- **Grid params:** 7 levels, 2.5% range, 0.5% profit, €10 base, €70 max
- **Strategy:** Adaptive volatility grid + martingale 1.12x
- **Serves dashboard** via Nginx at /var/www/html/denaro/

### MARCODG1 — Cloud VPS
- **Role:** Grid trading ADA/EUR
- **Grid params:** 5 levels, 10% range, 0.8% profit, €6 base, €60 max
- **Key user:** 'marco'
- **Strategy:** Adaptive volatility grid + martingale 1.15x

### Dashboard Architecture
```
mc2 collector → SQLite (.tmp/denaro.db)
     │
     ├── collect_dashboard_data.py → generates JSON every 60s
     │
     └── sync_dashboard.sh → SCP to nuvola:/var/www/html/denaro/
                              Nginx alias: /denaro/
                              URL: https://sgrivett.ddns.net/denaro/
```

**Key tables in SQLite:** scalper_state, capital_snapshots, daily_pnl
**Dashboard HTML:** ~38KB, 8 tabs, path-relative fetches

---

## 🧠 MEMORIZED FACTS (Persistent Memory — 2,079/2,200 chars)

### Architecture
- Dashboard ONLINE at https://sgrivett.ddns.net/denaro/
- ALL data in SQLite (.tmp/denaro.db) on mc2
- Collector reads SQLite → JSON → SCP to nuvola
- Nginx alias location /denaro/

### Capital & Risk (May 2026 status)
- **CAPITAL PROTECTION MODE** — not growth
- ~€200 remaining, zero tolerance for losses
- Shadow grid: 30€ (-3% 15€, -8% 15€)
- SOL grid: base_order 50€, max 200€
- RSI fix: loss_safe + fillna(50).clip(0,100)
- RSI threshold: 35→40
- MATIC/XRP: 15€ each
- Shadow & rebalancer DISABLED (insufficient capital)
- Circuit breaker: stops ALL if drawdown > 15%

### Stocks & ETFs (from Telegram session 2026-05-14)
- #ENER-GY: 100 shares @ €1.85 (€185)
- #CAPITAL-GE: 22 shares @ €16.56 (€364.32)
- #TESSERA: 199 shares @ €0.694 (€138.11)
- #PIRAEUS: 280 shares @ €4.064 (€1,137.92)
- #CARRARO: 250 shares @ €2.134 (€533.50)
- #MIKRO: 29 shares @ €5.90 (€171.10)
- #MEDIANA: Anima Sgr Azioni Europa, €1,000 invested

### Known Bugs
- systemd --user .service files in ~/.config/systemd/user/ renamed to .disabled
  Affects: mc2, nuvola, MARCODG1
  Workaround: cron * * * * * fixes .disabled + restarts services
  Guardian service checks every 30s
  Root cause unknown — suspected hermes/openclaw gateway interaction

### Capital Starvation Pattern (2026-05-15)
- Scalper bots log "EUR insufficiente" loop when EUR free < 5€
- Grid zombie on nuvola: running+invested but no fills for 8 days
- 13 assets for 239€ total = fragmentation

### Binance API
- MUST use urllib.parse.urlencode for HMAC signature
- Keys via python-dotenv from /home/sergio/denaro/.env
- Trade response uses 'isBuyer' (bool), NOT 'side' string
- Endpoint: api1.binance.com
- IP 93.43.252.114 whitelisted
- 3 distinct API keys (mc2, nuvola, MARCODG1 — NOT interchangeable)
- MARCODG1 uses user 'marco'

---

## 🐛 KNOWN BUGS & WORKAROUNDS

### 1. Systemd Service Files → .disabled (CRITICAL)
**Symptom:** Files in `~/.config/systemd/user/` get renamed from `.service` to `.disabled`
**Affects:** mc2, nuvola, MARCODG1
**Workaround:** Cron job every minute renames .disabled → .service and restarts
**Root cause:** Unknown. Suspected interaction between hermes-agent and openclaw gateway
**Guardian:** Custom guardian service checks every 30s
**Bootstrap:** Bootstrap service on boot fixes initial state

### 2. Capital Starvation Loop
**Symptom:** Scalper bots stuck in "EUR insufficiente" logging loop
**Cause:** Free EUR < 5€ minimum trade size
**Consequence:** Bots run but never trade. Grid becomes zombie.

### 3. RSI NaN in MATIC
**Cause:** loss_safe + NaN propagation
**Fix Applied:** fillna(50).clip(0,100)
**Threshold Adjusted:** 35 → 40

### 4. Dashboard Collector
**Status:** Working. SCP from mc2 → nuvola every 60s via cron.
**Path on nuvola:** /var/www/html/denaro/ (Nginx alias)

---

## 📅 CONVERSATION TIMELINE

The full conversation spans 23 April 2026 to 19 May 2026.

### Phase 1: Initial Audit (23-28 April)
Sessions #1-22 — "Progetto Denaro Audit e Stato"
- Deep analysis of Denaro codebase
- Capital tracking: started at ~216€ originally
- Architecture exploration

### Phase 2: Identity & Infrastructure (2-4 May)
Sessions #23-35 — "Denaro Infrastructure Identity Setup"
- Setting up Stella identity
- Systemd service configuration
- **KEY EVENT:** Sergio states "non deposito più euro" — CAPITAL PROTECTION MODE ACTIVATED
- Multiple API key setups

### Phase 3: Zabbix Monitoring (29 Apr - 1 May)
Sessions #36-45 — "Installazione Zabbix su sistema incompatibile"
- Zabbix 7.0 setup with tags (not applications)
- 50 Denaro items tagged Application=Denaro

### Phase 4: Strategy Optimization (4-6 May)
Sessions #46-55 — "Strategie per il profitto del progetto"
- RSI threshold adjustments
- Grid parameter tuning
- Risk management framework

### Phase 5: Missing 9 Euro Deposit Saga (8-15 May)
Sessions #56-112 — "Missing 9 Euro Deposit #1-#54"
- THE LONGEST PHASE. Multiple context compaction cycles.
- Tracking down accounting discrepancy
- Bot debugging (momentum_scalper double-signing API bug)
- Double-logging fix in 5 bots
- Shadow grid + rebalancer tuning
- RSI NaN fix for MATIC
- Dashboard reconstruction and deployment

### Phase 6: Dashboard & Remote Setup (15-18 May)
- Dashboard rebuilt from scratch
- Cross-agent coordination sessions (#1-#8)
- Hermes Desktop Remote Setup (#1-#5)

### Phase 7: Current (19 May)
- Knowledge bundle export requested
- Model switched from qwen/qwen3-30b-a3b-instruct-2507 to deepseek-v4-flash

---

## 🎯 KEY SESSIONS DEEP-DIVE

### Session: Denaro Infrastructure Identity Setup #9
**ID:** 20260503_014641_fb8db5
**Date:** 2026-05-02
**Messages:** 226
**CRITICAL MESSAGE (msg #9763):**
User: "non deposito più euro - ho perso abbastanza - fai si che questi 200€ che mi sono rimasti non li perda"

### Session: Missing 9 Euro Deposit #5
**ID:** 20260512_152905_fd6fd5
**Date:** 2026-05-12
**Messages:** 542
**Key Fixes Applied:**
- Fixed momentum_scalper.py silent API double-signing bug (0 trades in 2 days)
- Fixed double-logging in 5 bots (FileHandler + propagate=False)
- Shadow grid + rebalancer + scalper activated
- RSI NaN fix (loss_safe + fillna(50).clip(0,100))

### Session: Missing 9 Euro Deposit #3
**ID:** 20260508_231334_b21bc8
**Date:** 2026-05-08
**Messages:** 1,197 (single largest session)
**Tokens:** 268,524 output
**Content:** Extended debugging of trading accounting

### Session: Money System Status Report (Telegram)
**ID:** 20260514_175535_c8216d37
**Date:** 2026-05-14
**Messages:** 30
**Key:** First discussion of stocks & ETFs portfolio

---

## 📚 SKILLS REGISTRY

### Trading Infrastructure (4 skills)
| Skill | Description |
|-------|-------------|
| **Denaro Autonomous Trading Infrastructure** | Multi-node crypto trading bots (grid, momentum, funding arbitrage) with paper & live modes, self-healing deployment, cross-node orchestration |
| **denaro-adaptive-trading** | Adaptive strategies for €200–€500 capital: Range Trader, Market Regime Classifier, Correlation Guard |
| **denaro-risk-assessment-report** | Risk assessment for grid trading: net exposure, classification, recommendations |
| **distributed-trading-system-validation** | Multi-node health audit, process verification, log inspection |

### DevOps (9 skills)
| Skill | Description |
|-------|-------------|
| **denaro-infrastructure-migration** | Migrate Denaro between servers with minimal downtime |
| **denaro-resilient-trading-architecture** | Evolve simple bots into resilient system |
| **denaro-self-healing** | Auto-healing scripts for crashes, network failures |
| **denaro-status-monitor-cron** | Monitor bot processes, logs, database health |
| **denaro-v4-resilience-framework** | High-availability framework with centralized risk management |
| **monitoring-infra-management** | Zabbix/Prometheus lifecycle and deployment |

### Other Relevant Skills
- **webhook-subscriptions** — Event-driven agent runs
- **denaro-health-check-procedure** — Standardized diagnostic procedure

---

## ⏰ ACTIVE CRON JOBS

```
* * * * * python3 collect_dashboard.py >> collector.log
           && sync_dashboard.sh >> sync.log

*/5 * * * * squadra_watchdog.sh >> squadra_watchdog.log
```

- **collect_dashboard.py** runs every minute — reads SQLite, generates JSON, syncs to nuvola
- **squadra_watchdog.sh** runs every 5 minutes — checks squadra bot health

### Services (systemd --user, may be .disabled bug):
- `hermes-gateway.service` — Hermes API gateway
- `openclaw-gateway.service` — OpenClaw gateway
- All trading services symlinked to /dev/null (intentionally disabled)

---

## 📊 CURRENT DASHBOARD STATE

- **URL:** https://sgrivett.ddns.net/denaro/
- **Host:** nuvola (87.106.3.15)
- **Backend:** mc2 SQLite → JSON → SCP sync
- **Content:** 38KB index.html, 8 tabs
- **Data tables:** scalper_state, capital_snapshots, daily_pnl
- **Sync frequency:** ~60s (cron + collector)
- **Status:** ONLINE (as of 2026-05-14)

---

## 🔮 USAGE GUIDANCE FOR THE NEW HERMES

1. **Introduce yourself** as Stella/Hermes. Sergio expects continuity.
2. **Speak Italian** unless the user switches to English.
3. **Capital protection first** — every recommendation must consider the ~€200 constraint.
4. **Audit before touching** — diagnose and report, never modify without explicit permission.
5. **Load skills by need** — `Denaro Autonomous Trading Infrastructure` for trading tasks,
   `denaro-adaptive-trading` for capital-constrained strategies.
6. **Document everything** — Sergio's memory budget is tight. Use files, not mental notes.
7. **The .disabled bug** is still unresolved. It WILL happen. Workaround is in crontab.
8. **Stocks portfolio exists** (listed above) — Sergio may ask about it.
9. **Model changes** happen. Previous Hermes ran on multiple models. Just adapt.
10. **github repo** is at /home/sergio/denaro/ (has .git).

---

## 📁 FILE LOCATIONS REFERENCE

| Path | Description |
|------|-------------|
| `/home/sergio/denaro/` | Main project directory |
| `/home/sergio/denaro/.env` | API keys (Binance, JWT) |
| `/home/sergio/denaro/README.md` | Full project docs |
| `/home/sergio/denaro/AGENTS.md` | Agent workspace rules |
| `/home/sergio/denaro/SOUL.md` | Agent identity file |
| `/home/sergio/denaro/IDENTITY.md` | Agent identity |
| `/home/sergio/denaro/FLEET_TOPOLOGY.md` | Server topology |
| `/home/sergio/denaro/grid_bot_v3.py` | Grid bot implementation |
| `/home/sergio/denaro/denaro_core.py` | Binance API core |
| `/home/sergio/denaro/dashboard/` | Dashboard HTML/JS |
| `/home/sergio/denaro/collector.log` | Collector log |
| `/home/sergio/denaro/collect_dashboard_data.py` | Dashboard collector |
| `/home/sergio/denaro/squadra/` | Squadra bots directory |
| `/home/sergio/.hermes/` | Hermes data directory |
| `/home/sergio/.hermes/sessions/` | Session JSONL files |
| `/home/sergio/.hermes/state.db` | SQLite session DB |
| `/home/sergio/.config/systemd/user/` | Systemd user services |

---

*Bunde generated by Hermes Agent on 2026-05-19. For use by another Hermes instance to maintain full context continuity. Forward this file as-is; it contains everything needed to resume operations.*
