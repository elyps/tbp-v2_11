# Fix Git Conflict auf dem Server

## Problem
```
error: Your local changes to the following files would be overwritten by merge:
        portfolio_state.json
Please commit your changes or stash them before you merge.
```

## Ursache
Die Datei `portfolio_state.json` wird auf dem Server vom Bot laufend aktualisiert und hat lokale Änderungen, die beim Git Pull überschrieben werden würden.

## Lösung

### Option 1: Stash (Empfohlen - Behält die Datei)
```bash
# Auf dem Server ausführen:
cd /pfad/zum/tbp-v2_11

# 1. Stoppe den Bot (falls er läuft)
pkill -f run_paper_trading.py

# 2. Stash die lokalen Änderungen
git stash

# 3. Pull die neuesten Änderungen
git pull origin dev

# 4. Stelle sicher, dass portfolio_state.json nicht getrackt wird
git rm --cached data/portfolio_state.json 2>/dev/null || true

# 5. Prüfe ob die Datei ignoriert wird
git check-ignore -v data/portfolio_state.json

# 6. Optional: Hole die Datei zurück (falls benötigt)
git stash pop || true

# 7. Starte den Bot neu
python run_paper_trading.py &
```

### Option 2: Discard (Schnell - Verwirft lokale Änderungen)
```bash
# Auf dem Server ausführen:
cd /pfad/zum/tbp-v2_11

# 1. Stoppe den Bot
pkill -f run_paper_trading.py

# 2. Verwerfe lokale Änderungen an portfolio_state.json
git checkout -- data/portfolio_state.json 2>/dev/null || true

# 3. Entferne aus Git-Tracking (falls getrackt)
git rm --cached data/portfolio_state.json 2>/dev/null || true

# 4. Pull die Änderungen
git pull origin dev

# 5. Portfolio zurücksetzen
python helper_scripts/reset_portfolio.py

# 6. Bot neu starten
python run_paper_trading.py &
```

### Option 3: Force (Wenn nichts anderes funktioniert)
```bash
# WARNUNG: Verwirft ALLE lokalen Änderungen!
cd /pfad/zum/tbp-v2_11

# 1. Stoppe den Bot
pkill -f run_paper_trading.py

# 2. Backup der wichtigen Dateien
cp data/trading_bot.db data/trading_bot.db.backup
cp data/portfolio_state.json data/portfolio_state.json.backup

# 3. Hard Reset auf Remote
git fetch origin
git reset --hard origin/dev

# 4. Entferne portfolio_state.json aus Tracking
git rm --cached data/portfolio_state.json 2>/dev/null || true

# 5. Stelle Datenbank wieder her
cp data/trading_bot.db.backup data/trading_bot.db

# 6. Portfolio zurücksetzen
python helper_scripts/reset_portfolio.py

# 7. Bot neu starten
python run_paper_trading.py &
```

## Dauerhafte Lösung

Um das Problem zukünftig zu vermeiden:

```bash
# Auf dem Server:
cd /pfad/zum/tbp-v2_11

# 1. Entferne portfolio_state.json aus Git (falls noch getrackt)
git rm --cached data/portfolio_state.json 2>/dev/null || true
git rm --cached portfolio_state.json 2>/dev/null || true

# 2. Committe die Änderung (wenn nötig)
git status
# Falls Änderungen vorhanden:
git add .gitignore
git commit -m "Remove portfolio_state.json from tracking"

# 3. Prüfe .gitignore
grep -E "portfolio_state|data/" .gitignore

# Sollte enthalten:
# data/
# portfolio_state.json
```

## Automatisches Update-Script

Erstelle ein Script für zukünftige Updates:

```bash
# helper_scripts/update_bot.sh (existiert bereits)
#!/bin/bash

echo "[INFO] Stoppe Bot..."
pkill -f run_paper_trading.py

echo "[INFO] Sichere Daten..."
cp data/trading_bot.db data/trading_bot.db.backup 2>/dev/null || true

echo "[INFO] Stash lokale Änderungen..."
git stash

echo "[INFO] Pull neueste Änderungen..."
git pull origin dev

echo "[INFO] Entferne Runtime-Dateien aus Tracking..."
git rm --cached data/portfolio_state.json 2>/dev/null || true
git rm --cached data/*.db 2>/dev/null || true

echo "[INFO] Starte Bot neu..."
nohup python run_paper_trading.py > logs/bot.log 2>&1 &

echo "[OK] Bot erfolgreich aktualisiert!"
```

## Prüfung

Nach der Lösung sollte Folgendes gelten:

```bash
# 1. Datei ist ignoriert
git check-ignore -v data/portfolio_state.json
# Output: .gitignore:2:data/    data/portfolio_state.json

# 2. Datei wird nicht getrackt
git ls-files | grep portfolio_state.json
# Output: (leer)

# 3. Git Status ist sauber
git status
# Output: On branch dev, nothing to commit, working tree clean

# 4. Bot läuft
ps aux | grep run_paper_trading.py
```

## Wichtige Hinweise

- ⚠️ **IMMER den Bot stoppen** vor Git-Operationen
- 💾 **Backup der Datenbank** vor größeren Änderungen
- 🔍 **Prüfe Git Status** nach dem Update
- 🚀 **Bot neu starten** nach erfolgreicher Aktualisierung
- 📝 **Logs checken** ob der Bot korrekt startet

## Häufige Fehler

### "portfolio_state.json still tracked"
```bash
git rm --cached data/portfolio_state.json
git commit -m "Remove portfolio_state.json from tracking"
git push origin dev
```

### "Bot startet nicht nach Update"
```bash
# Prüfe Logs
tail -100 logs/trading_bot.log

# Prüfe Python-Fehler
python run_paper_trading.py  # Im Vordergrund testen

# Portfolio zurücksetzen
python helper_scripts/reset_portfolio.py
```

### "Datenbank ist korrupt"
```bash
# Restore Backup
cp data/trading_bot.db.backup data/trading_bot.db

# Oder neu starten
python helper_scripts/reset_database.py
python helper_scripts/reset_portfolio.py
```
