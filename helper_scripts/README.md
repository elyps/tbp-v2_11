# Helper Scripts

Hilfsskripte für Debugging, Testing, Wartung und Server-Management.

## 🔍 Debug & Check Scripts

### Portfolio & Datenbank
- **`check_positions.py`** - Zeigt offene Positionen und Trades
- **`check_db.py`** - Prüft Datenbank-Status
- **`check_schema.py`** - Prüft Datenbank-Schema
- **`check_all_data.py`** - Vollständige Datenbank-Analyse
- **`view_database.py`** - Interaktive Datenbank-Ansicht
- **`view_trades.py`** - Zeigt Trade-Historie

### Trading & Signale
- **`check_sells.py`** - Prüft Verkaufssignale
- **`check_errors.py`** - Zeigt Fehler im Log
- **`check_dashboard_issue.py`** - Dashboard-Probleme debuggen
- **`debug_signals.py`** - Signal-Generierung debuggen
- **`debug_trades.py`** - Trade-Ausführung debuggen
- **`debug_config.py`** - Konfigurationswerte prüfen

## 🧪 Test Scripts

- **`test_init_only.py`** - Testet nur Bot-Initialisierung
- **`test_bot_init.py`** - Vollständiger Init-Test
- **`test_bot_start.py`** - Testet Bot-Start mit Loop
- **`test_full_cycle.py`** - Testet Reset + Init + Start
- **`test_dashboard.py`** - Dashboard ohne Loop testen
- **`test_dashboard_data.py`** - Dashboard-Daten prüfen
- **`test_portfolio.py`** - Portfolio-Funktionen testen

## 🗄️ Datenbank Scripts

### Migration & Setup
- **`migrate_to_sqlite.py`** - Migriert alte JSON-Daten zu SQLite
- **`migrate_add_columns.py`** - Fügt Spalten zu Tabellen hinzu
- **`fix_database.py`** - Repariert Datenbank-Probleme

### Verwaltung
- **`reset_database.py`** - Setzt Datenbank komplett zurück
- **`view_database.py`** - Datenbank-Viewer
- **`view_trades.py`** - Trade-Viewer

## 📊 Monitoring Scripts

- **`monitor_bot.py`** - Einfaches Bot-Monitoring
- **`monitor_bot_advanced.py`** - Erweitertes Monitoring
- **`monitor_learning.py`** - ML-Training überwachen

## 🔧 Konfiguration & Setup

- **`initialize_portfolio_with_coins.py`** - Portfolio mit Startpositionen initialisieren
- **`switch_config.py`** - Zwischen Konfigurationen wechseln

## 🖥️ Server Management Scripts

### Deployment
- **`deploy-to-server.sh`** - Deployed Bot auf Server
- **`update_bot.sh`** - Updated Bot auf Server (pullt, stoppt, startet)
- **`manage_bot.sh`** - Server-Bot-Verwaltung

### Verwendung auf dem Server
```bash
# Bot updaten und neu starten
./helper_scripts/update_bot.sh

# Bot manuell verwalten
./helper_scripts/manage_bot.sh
```

## 🏃 Training Scripts (Legacy)

Alte Training-Varianten (verwende stattdessen `train_comprehensive_model.py` im Root):
- **`train_model.py`** - Basis-Training
- **`train_optimized_model.py`** - Optimiertes Training
- **`train_premium_model.py`** - Premium-Features

## 📝 Verwendung

Die meisten Skripte können direkt ausgeführt werden:

```bash
# Von Root aus
python helper_scripts/check_positions.py
python helper_scripts/test_init_only.py
python helper_scripts/view_database.py
```

Oder aus dem helper_scripts Ordner:
```bash
cd helper_scripts
python check_positions.py
```

## ⚠️ Hinweise

- Diese Skripte sind **nur für Entwicklung und Debugging**
- **Nicht im Produktivbetrieb** verwenden (außer Server-Management-Skripte)
- Einige Skripte können Datenbank-Änderungen vornehmen
- Immer vorher Backup erstellen bei kritischen Operationen
