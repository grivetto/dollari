# 2026-03-22 - Report Serale

- **Richiesta**: Sergio ha chiesto di automatizzare il mantenimento delle risorse (FLASH-UNIT, LIQUID-HARV, NEURAL-PLS).
- **Azione**: 
  - Creato `fleet_guardian.py`: un demone di monitoraggio che controlla ogni 30 secondi se i bot principali sono attivi.
  - Se un bot (come LIQUID-HARV o NEURAL-PLS) crasha o viene chiuso, il Guardian lo riavvia istantaneamente.
  - Avviato `fleet_guardian.py` in background.
  - Impostato un cron job di persistenza per assicurarsi che il Guardian stesso non smetta mai di girare.
  - Aggiornato `HEARTBEAT.md` con nuove linee guida per il monitoraggio.
- **Risultato**: LIQUID-HARV e NEURAL-PLS sono stati rianimati con successo e sono ora ONLINE.
