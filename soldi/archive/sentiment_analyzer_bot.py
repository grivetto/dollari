import gc
import gc
# Logica: Analisi simulata del sentiment social per anticipare spike
import time, logging
logging.basicConfig(level=logging.INFO, filename="sentiment.log")
while True:
    logging.info("Sentiment: Positive 65% - Bullish bias")
    gc.collect()
    time.sleep(300)
