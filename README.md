# 🚀 DENARO: Autonomous Trading Infrastructure

DENARO is a distributed, self-healing trading system designed for survival, protection, and professional growth. It has evolved from a collection of individual bots into a closed-loop autonomous architecture.

## 🏗 Architecture

The system is distributed across three specialized nodes to ensure redundancy and separation of concerns:

### 1. NUVOLA (Control & Execution Node)
*   **Role**: The central "Brain" and primary execution hub.
*   **Core Components**:
    *   **Grid Bot v3**: High-frequency, self-healing grid strategy with adaptive order sizing.
    *   **Optimization Agent (`optimizer.py`)**: The "Learner". It analyzes real-time volatility (ATR) and dynamically updates the grid spreads in `grid_config_nuvola.json` to maximize profit.
    *   **Stability Guardian (`guardian_v3.py`)**: The "Watchdog". It monitors bot health and ensures zero-downtime execution via systemd.
    *   **Infrastructure**: Fully managed by `systemd` for automatic recovery and centralized logging.

### 2. MC2 (Development & Heavy-Lift Node)
*   **Role**: Physical server (16GB RAM) dedicated to R&D.
*   **Purpose**: Sandbox for strategy development, backtesting, and heavy data processing before deploying to the cloud.

### 3. MARCODG1 (Auxiliary Execution Node)
*   **Role**: Backup execution node.
*   **Focus**: Redundant grid trading for diversified risk.

## 🧠 The Autonomous Loop (Self-Learning)

Unlike traditional bots, DENARO implements a continuous feedback loop:
`TRADING` $\rightarrow$ `ANALYSIS` $\rightarrow$ `OPTIMIZATION` $\rightarrow$ `REDEPLOYMENT`

1.  **Execution**: Bots place orders based on the current dynamic configuration.
2.  **Analysis**: The `optimizer` analyzes the last 24h of price action for each symbol.
3.  **Optimization**: The system calculates the optimal spread based on current volatility (ATR) and updates the config.
4.  **Real-time Adaptation**: The bots detect config changes and adjust their grid parameters instantly without needing a restart.

## 🛡 Safety & Survival (Sopravvivenza)
*   **Circuit Breaker**: Integrated loss limits to prevent catastrophic drawdowns.
*   **Adaptive Sizing**: Order sizes are calculated based on available balance to prevent "Insufficient Funds" errors.
*   **Self-Healing**: Automatic synchronization of open orders on startup to prevent duplicate positions.
*   **Sovereign Infrastructure**: Managed via SSH and systemd for maximum control and reliability.

---
*Developed by Sergio - "Sopravvivenza $\rightarrow$ Protezione $\rightarrow$ Intelligenza $\rightarrow$ Professionalità"*
