# Trading Bot v2.11 - Paper Trading (100€ Challenge)

Ein KI-gestützter Trading-Bot für Kryptowährungen mit Machine Learning Integration.

## 🚀 Schnellstart

### 1. Portfolio auf 100€ zurücksetzen
```bash
python reset_portfolio.py
```

### 2. Bot starten
```bash
python run_paper_trading.py
```

### 3. Dashboard überwachen
```bash
python paper_trading_dashboard.py
```

## 📁 Projektstruktur

### Haupt-Skripte (Root)
- **`run_paper_trading.py`** - Startet den Bot im Paper Trading Modus (100€)
- **`paper_trading_dashboard.py`** - Live-Dashboard für Performance-Monitoring
- **`reset_portfolio.py`** - Setzt Portfolio auf 100€ zurück
- **`train_comprehensive_model.py`** - Trainiert das ML-Modell
- **`main.py`** - Haupt-Einstiegspunkt (alternatives Start-Skript)
- **`reset_bot.py`** - Vollständiger Bot-Reset

### Module (`trading_bot/`)
- **`bot.py`** - Haupt-Bot-Logik
- **`ml_model.py`** - Machine Learning Modell
- **`strategy.py`** - Trading-Strategien
- **`risk_management.py`** - Risikomanagement
- **`data_provider.py`** - Marktdaten-Provider
- **`database.py`** - SQLite Datenbank-Manager
- **`indicators.py`** - Technische Indikatoren
- **`exchange.py`** - Börsen-Schnittstelle
- **`continuous_learning.py`** - Kontinuierliches Lernsystem

### Enhanced Pipeline (`trader/`)
Companion Codex Pipeline mit erweiterten Features
- `data/` - Feature Engineering
- `signals/` - Signal-Generierung
- `sizing/` - Position Sizing
- `risk/` - Erweiterte Risiko-Regeln
- `live/` - Live Trading & Broker

### Hilfsskripte (`helper_scripts/`)
Debug, Test und Wartungs-Skripte:
- **Debug**: `debug_*.py`, `check_*.py`
- **Tests**: `test_*.py`
- **Datenbank**: `migrate_*.py`, `view_*.py`, `fix_database.py`
- **Monitoring**: `monitor_*.py`
- **Server**: `deploy-to-server.sh`, `update_bot.sh`, `manage_bot.sh`

### Dokumentation (`docs/`)
- `env.example.txt` - Beispiel-Umgebungsvariablen

## 🔧 Konfiguration

### API Keys (`.env`)
```bash
ALPHA_VANTAGE_API_KEY=your_key
NEWS_API_KEY=your_key
CRYPTOCOMPARE_API_KEY=your_key
```

### Bot-Konfiguration (`trading_bot/config.py`)
- `initial_balance`: Startkapital (Standard: 100€)
- `risk_per_trade`: Risiko pro Trade (1%)
- `timeframe`: Zeitrahmen für Analyse (1h)

## 📊 Workflow

### Erstes Setup
1. **Modell trainieren**:
   ```bash
   python train_comprehensive_model.py
   ```

2. **Portfolio initialisieren**:
   ```bash
   python reset_portfolio.py
   ```

3. **Bot starten**:
   ```bash
   python run_paper_trading.py
   ```

### Täglicher Betrieb
```bash
# Auf dem Server
./helper_scripts/update_bot.sh   # Pullt Updates und startet Bot neu
```

## 🗄️ Datenbank

SQLite-Datenbank (`trading_bot.db`) mit folgenden Tabellen:
- `portfolio` - Portfolio-Status
- `trades` - Trade-Historie
- `positions` - Offene Positionen
- `training_data` - ML Training Samples
- `model_performance` - ML Modell-Metriken
- `news` - News & Sentiment
- `signals` - Generierte Signale

## 🧪 Testing & Debugging

### Portfolio prüfen
```bash
python helper_scripts/check_positions.py
```

### Datenbank ansehen
```bash
python helper_scripts/view_database.py
```

### Bot-Initialisierung testen
```bash
python helper_scripts/test_init_only.py
```

## 📈 Features

- ✅ **Machine Learning** - Prädiktive Modelle mit kontinuierlichem Lernen
- ✅ **Technische Indikatoren** - RSI, MACD, Bollinger Bands, etc.
- ✅ **Risikomanagement** - Stop-Loss, Take-Profit, Position Sizing
- ✅ **Multi-Strategy** - Trend Following, Mean Reversion, ML-basiert
- ✅ **Paper Trading** - Risikofreies Testen
- ✅ **Live Dashboard** - Echtzeit-Performance-Monitoring
- ✅ **SQLite DB** - Persistente Datenspeicherung
- ✅ **Continuous Learning** - Modell lernt aus eigenen Trades

## 🛠️ Wartung

### Portfolio zurücksetzen
```bash
python reset_portfolio.py
```
Setzt:
- Portfolio auf 100€
- Löscht offene Positionen
- Löscht offene Trades
- Aktualisiert `portfolio_state.json`

### Modell neu trainieren
```bash
python train_comprehensive_model.py
```

### Datenbank bereinigen
```bash
python helper_scripts/fix_database.py
```

## 📝 Logs

Logs werden in `logs/trading_bot.log` gespeichert.

## ⚠️ Wichtige Hinweise

1. **Immer Portfolio zurücksetzen** vor dem Start:
   ```bash
   python reset_portfolio.py
   ```

2. **Modell trainieren** vor dem ersten Start:
   ```bash
   python train_comprehensive_model.py
   ```

3. **Nicht in Git committen**:
   - `trading_bot.db` (Datenbank)
   - `portfolio_state.json` (Portfolio-State)
   - `*.log` (Logs)
   - `__pycache__/` (Python Cache)

## 🤝 Contributing

Dieses Projekt ist ein privates Trading-Bot-Experiment.

## 📄 Lizenz

Privates Projekt - Alle Rechte vorbehalten.
