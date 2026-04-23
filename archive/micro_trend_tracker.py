import gc
import time
import logging
import random
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - MICRO-TREND - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Avviato Micro-Trend Tracker - Target mini-trend su timeframe 1m per scalping rapido (Zero-OOM).")
    import gc
    while True:
        gc.collect()
        try:
            # Simulazione rilevamento trend
            momentum = random.uniform(-10.0, 10.0)
            if momentum > 7.5:
                logger.info(f"Forte mini-trend rialzista (Momentum: {momentum:.2f}). Apro long scalping.")
            elif momentum < -7.5:
                logger.info(f"Forte mini-trend ribassista (Momentum: {momentum:.2f}). Apro short scalping.")
            else:
                logger.debug("Trend laterale. Nessuna operazione.")
            
            with open("micro_trend_status.json", "w") as f:
                f.write(f'{{"momentum": {momentum:.2f}, "timestamp": {time.time()}}}')
            
            time.sleep(20)
        except Exception as e:
            logger.error(f"Errore: {e}")
            logger.info("💗 Heartbeat OK.")
            time.sleep(60)

if __name__ == "__main__":
    main()
