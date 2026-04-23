#!/bin/bash
# Start Realistic Denaro System — Target €3-5/giorno

echo "🚀 AVVIO SISTEMA REALISTICO DENARO"
echo "==================================="
echo ""

# 1. Ferma tutto il caos precedente
echo "1️⃣ Fermando bot vecchi..."
sudo pkill -f "mev_sandwich\|phantom_maker\|vampire_grid\|sniper_squad" 2>/dev/null
sleep 2

# 2. Stato servizi essenziali
echo ""
echo "2️⃣ Controllo servizi core:"
services=("denaro-ai-risk" "denaro-crisis" "denaro-delta-neutral" "denaro-telegram" "denaro-dashboard")
for svc in "${services[@]}"; do
    if sudo systemctl is-active --quiet $svc; then
        echo "  ✅ $svc"
    else
        echo "  🔴 $svc — avvio..."
        sudo systemctl start $svc
    fi
done

# 3. Avvia Grid Bot Realistico
echo ""
echo "3️⃣ Avvio Grid Bot Realistico (€3-5/giorno)..."
sudo systemctl start denaro-realistic-grid

# 4. Avvia Target Tracker
echo "4️⃣ Avvio Target Tracker..."
sudo systemctl start denaro-target-tracker

# 5. Stato finale
echo ""
echo "==================================="
echo "📊 STATO SISTEMA:"
sleep 2
sudo systemctl list-units denaro-* --type=service --state=running --no-pager 2>/dev/null | grep "loaded active" || echo "Controlla: sudo systemctl status denaro-*"

echo ""
echo "💰 Target: €3-5/giorno (Fase 1)"
echo "📈 Crescita: Automatica quando capitale >€500"
echo "📱 Alert: Telegram @Sergiotrdxbot"
echo ""
echo "Log in tempo reale:"
echo "  tail -f /home/sergio/.openclaw/workspace/denaro/REALISTIC_GRID.log"
