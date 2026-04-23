with open("mexc_nano_squad.py", "r") as f:
    code = f.read()

# Add JSON and OS if missing (os is there)
code = code.replace("import pandas as pd", "import pandas as pd\nimport json")

# Find the sell logic:
sell_logic = """                        if LIVE_TRADING:
                            try:
                                mexc.create_market_sell_order(symbol, qty)
                                logger.info(f"✅ [LIVE] VENDUTO {symbol}. Profitto netto incassato in USDT!")
                                
                                # Calcolo Elemosina
                                profit = (current_price - entry_price) * qty
                                elemosina = profit * 0.33
                                try:
                                    vault_file = '/home/sergio/.openclaw/workspace/denaro/vault.json'
                                    with open(vault_file, 'r') as f: v_data = json.load(f)
                                    v_data['GARIBAN_TRACKER'] = v_data.get('GARIBAN_TRACKER', 0.0) + elemosina
                                    v_data['LOCKED_EUR'] = v_data.get('LOCKED_EUR', 0.0) + elemosina
                                    with open(vault_file, 'w') as f: json.dump(v_data, f)
                                    logger.info(f"🤲 [GARIBAN MEXC] Prelevati {elemosina:.4f} USDT di profitto per l'Elemosina!")
                                except Exception as ve:
                                    logger.error(f"Errore aggiornamento Elemosina: {ve}")

                                del active_trades[symbol]
                            except Exception as e:
"""

# We need to replace the old sell logic block
# old:
#                        if LIVE_TRADING:
#                            try:
#                                mexc.create_market_sell_order(symbol, qty)
#                                logger.info(f"✅ [LIVE] VENDUTO {symbol}. Profitto netto incassato in USDT!")
#                                del active_trades[symbol]
#                            except Exception as e:

import re
code = re.sub(r'if LIVE_TRADING:\n\s+try:\n\s+mexc.create_market_sell_order\(symbol, qty\)\n\s+logger.info\(f"✅ \[LIVE\] VENDUTO \{symbol\}\. Profitto netto incassato in USDT!"\)\n\s+del active_trades\[symbol\]\n\s+except Exception as e:', sell_logic, code)

# Let's also do it for the simulation mode so he sees it testing
sim_sell_logic = """                        else:
                            logger.info(f"✅ [SIMULAZIONE] Chiusura posizione su {symbol} completata con successo.")
                            profit = (current_price - entry_price) * qty
                            elemosina = profit * 0.33
                            try:
                                vault_file = '/home/sergio/.openclaw/workspace/denaro/vault.json'
                                with open(vault_file, 'r') as f: v_data = json.load(f)
                                v_data['GARIBAN_TRACKER'] = v_data.get('GARIBAN_TRACKER', 0.0) + elemosina
                                v_data['LOCKED_EUR'] = v_data.get('LOCKED_EUR', 0.0) + elemosina
                                with open(vault_file, 'w') as f: json.dump(v_data, f)
                                logger.info(f"🤲 [GARIBAN MEXC] (Simulato) Aggiunti {elemosina:.4f} USDT all'Elemosina/Vault!")
                            except: pass
                            del active_trades[symbol]
"""
code = re.sub(r'else:\n\s+logger.info\(f"✅ \[SIMULAZIONE\] Chiusura posizione su \{symbol\} completata con successo."\)\n\s+del active_trades\[symbol\]', sim_sell_logic, code)


with open("mexc_nano_squad.py", "w") as f:
    f.write(code)
print("MEXC Elemosina patched.")
