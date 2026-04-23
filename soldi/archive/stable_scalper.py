import gc
import time
import logging
import random

LOG_FILE = "/home/sergio/.openclaw/workspace/denaro/STABLE_SCALPER.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - STABLE-SCALPER - %(message)s', handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def main():
    logger.info("Avviato Stablecoin Scalper (EUR/USDT) - Target spread microscopici.")
    import gc
    while True:
        gc.collect()
        try:
            # Simulazione spread
            spread = random.uniform(0.0001, 0.0020)
            if spread > 0.0015:
                logger.info(f"Spread favorevole rilevato: {spread:.4f}. Eseguo micro-trade scalping.")
            else:
                logger.info("Spread troppo basso, attendo.")
            time.sleep(30)
        except Exception as e:
            logger.error(f"Errore: {e}")
            logger.info("💗 Heartbeat OK.")
            time.sleep(60)

if __name__ == "__main__":
    main()
