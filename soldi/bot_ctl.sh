#!/bin/bash
# Gestione Trading Bot - Standard o Aggressivo
# Uso: ./bot_ctl.sh [aggressive|standard] [start|stop|restart|status|logs]

BOT_TYPE="${1:-aggressive}"
ACTION="${2:-status}"

if [ "$BOT_TYPE" = "aggressive" ] || [ "$BOT_TYPE" = "agg" ]; then
    SERVICE="binance-bot-aggressive.service"
    NAME="AGGRESSIVO"
else
    SERVICE="binance-bot.service"
    NAME="STANDARD"
fi

case "$ACTION" in
    start)
        # Ferma l'altro bot se running
        if [ "$BOT_TYPE" = "aggressive" ]; then
            systemctl stop binance-bot.service 2>/dev/null
        else
            systemctl stop binance-bot-aggressive.service 2>/dev/null
        fi
        systemctl start $SERVICE
        echo "🚀 Bot $NAME avviato"
        systemctl status $SERVICE --no-pager
        ;;
    stop)
        systemctl stop $SERVICE
        echo "🛑 Bot $NAME fermato"
        ;;
    restart)
        systemctl restart $SERVICE
        echo "🔄 Bot $NAME riavviato"
        systemctl status $SERVICE --no-pager
        ;;
    status)
        echo "📊 Bot $NAME:"
        systemctl status $SERVICE --no-pager
        ;;
    logs)
        echo "📋 Log Bot $NAME (Ctrl+C per uscire):"
        journalctl -u $SERVICE -f --no-pager
        ;;
    *)
        echo "Uso: $0 [aggressive|standard] [start|stop|restart|status|logs]"
        echo ""
        echo "Esempi:"
        echo "  ./bot_ctl.sh aggressive start   # Avvia bot aggressivo"
        echo "  ./bot_ctl.sh standard logs      # Log bot standard"
        echo "  ./bot_ctl.sh agg status         # Stato bot aggressivo"
        exit 1
        ;;
esac
