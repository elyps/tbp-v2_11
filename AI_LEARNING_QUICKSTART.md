# 🚀 AI Learning Quick Start Guide

Starte den Bot in 5 Minuten mit automatischem Lernen aus News und Marktdaten!

## 1. API Keys einrichten (2 Min)

Erstelle `.env` im Projekt-Root:

```bash
# Copy template
cp docs/env.example.txt .env

# Edit with your keys
nano .env  # oder notepad .env (Windows)
```

**Minimum (Trading only)**:
```bash
KRAKEN_API_KEY=your_kraken_key
KRAKEN_API_SECRET=your_kraken_secret
```

**Empfohlen (mit AI Learning)**:
```bash
KRAKEN_API_KEY=your_kraken_key
KRAKEN_API_SECRET=your_kraken_secret
NEWSAPI_KEY=your_newsapi_key           # https://newsapi.org (kostenlos)
CRYPTOCOMPARE_KEY=your_cryptocompare_key
COINDESK_API_KEY=your_coindesk_key
```

## 2. Portfolio vorbereiten (1 Min)

```bash
# Reset auf €100
python helper_scripts/reset_portfolio.py
```

## 3. Bot starten (1 Min)

```bash
# Terminal 1: Bot mit AI Learning
python run_paper_trading.py

# Terminal 2: Trading Dashboard
python paper_trading_dashboard.py

# Terminal 3: AI Learning Dashboard
python ai_learning_dashboard.py
```

## 4. Was passiert jetzt?

### Sofort
- ✅ Bot startet und generiert Trading-Signale
- ✅ ML-Modell lädt (falls vorhanden)
- ✅ AI Learning Engine startet im Hintergrund

### Nach 1 Stunde
- 📊 Erste Marktdaten gesammelt (OHLCV + Indikatoren)
- 🔄 Training-Samples in Datenbank

### Nach 4 Stunden
- 📰 Erste News gesammelt (CoinDesk, NewsAPI, CryptoCompare)
- 💭 Sentiment-Analyse durchgeführt
- 🗄️ News in Datenbank gespeichert

### Nach 24 Stunden
- 🧠 Erstes Auto-Retraining (wenn min. 100 Samples)
- 📈 Model-Performance in Dashboard sichtbar
- ✨ Genauere Vorhersagen durch gelernte Patterns

## 5. Dashboards verstehen

### Trading Dashboard (`paper_trading_dashboard.py`)
```
╔═══════════════════════════════════════════════════╗
║  🚀 PAPER TRADING DASHBOARD (100€ Challenge) 🚀   ║
╚═══════════════════════════════════════════════════╝

  PERFORMANCE
  ├─ Startkapital:      €100.00
  ├─ Aktuelles Kapital:   €105.50
  └─ Gewinn / Verlust:    €5.50 (+5.50%)

  STATISTIKEN
  ├─ Trades gesamt:       12
  ├─ Gewinn-Trades:       8
  └─ Win-Rate:            66.7%
```

### AI Learning Dashboard (`ai_learning_dashboard.py`)
```
╔════════════════════════════════════════════════════════╗
║      🧠  AI LEARNING DASHBOARD - Live Performance  🧠  ║
╚════════════════════════════════════════════════════════╝

  📊 MODEL PERFORMANCE
  ├─ Aktuelle Accuracy:    72.5%
  ├─ Training Samples:     1,247
  ├─ Letztes Training:     2025-10-22 14:30
  └─ Trend:                📈 +3.2%

  📚 TRAINING DATEN
  ├─ Total Samples:        1,247
  ├─ Verkauf (0):          312
  ├─ Halten (1):           523
  └─ Kauf (2):             412

  📰 NEWS & SENTIMENT
  ├─ News (24h):           47
  ├─ Ø Sentiment:          +0.18 (Positiv)
  ├─ Positiv:              23
  ├─ Neutral:              18
  └─ Negativ:              6
```

## 6. Überprüfen ob es funktioniert

### Check 1: Bot läuft
```bash
# Logs checken
tail -f logs/trading_bot.log | grep "AI Learning"

# Sollte zeigen:
# ✓ AI Learning Engine initialisiert
# 🧠 AI Learning Engine gestartet (News + Marktdaten)
```

### Check 2: News werden gesammelt
```bash
python -c "
from trading_bot.database import get_database
db = get_database()
news = db.get_recent_news('BTC', hours=24)
print(f'News gefunden: {len(news)}')
"
```

### Check 3: Training-Daten wachsen
```bash
python -c "
from trading_bot.database import get_database
db = get_database()
df = db.get_training_data(limit=10000)
print(f'Training Samples: {len(df)}')
"
```

### Check 4: Model wird besser
```bash
python -c "
from trading_bot.database import get_database
db = get_database()
perf = db.get_model_performance_history(limit=5)
for p in perf:
    print(f\"{p['timestamp'][:16]} - {p['accuracy']*100:.1f}%\")
"
```

## 7. Ohne News-APIs starten

Falls du keine News-API-Keys hast:

```python
# In trading_bot/config.py
DEFAULT_SETTINGS = {
    # ...
    'enable_news_learning': False,  # ← Deaktiviere News
    'enable_market_learning': True,  # ← Nur Marktdaten
}
```

Der Bot funktioniert trotzdem, lernt aber nur aus:
- ✅ Marktdaten (OHLCV)
- ✅ Technischen Indikatoren
- ✅ Eigenen Trades

**Accuracy-Unterschied**: ~3-6% niedriger ohne News-Sentiment

## 8. Einstellungen anpassen

### Häufiger sammeln (mehr Daten)
```python
DEFAULT_SETTINGS = {
    'news_fetch_interval_hours': 2,        # Alle 2h statt 4h
    'market_data_fetch_interval_hours': 0.5,  # Alle 30min statt 1h
}
```

### Öfter trainieren
```python
DEFAULT_SETTINGS = {
    'retrain_frequency_hours': 12,  # Alle 12h statt 24h
    'min_samples_retrain': 50,      # Min. 50 Samples statt 100
}
```

### Aggressiveres Lernen
```python
ML_SETTINGS = {
    'n_estimators': 300,      # Mehr Trees (Standard: 200)
    'max_depth': 10,          # Tiefere Trees (Standard: 7)
    'learning_rate': 0.03,    # Langsameres Lernen (Standard: 0.05)
}
```

## 9. Erste 24 Stunden

### Stunde 0-1: Initial Setup
- Bot startet
- Erste Signale generiert
- Erste Trades ausgeführt

### Stunde 1-4: Daten sammeln
- Marktdaten jede Stunde
- Indikatoren berechnen
- Training-Samples erstellen

### Stunde 4: Erste News
- CoinDesk abgefragt
- NewsAPI abgefragt
- Sentiment analysiert
- News in DB gespeichert

### Stunde 8-24: Continuous Collection
- News alle 4h
- Marktdaten jede Stunde
- >100 Training-Samples gesammelt

### Stunde 24: Erstes Retraining
- Model lädt alle Samples
- Feature Engineering
- Training (XGBoost)
- Performance-Evaluation
- Neues Modell gespeichert
- Accuracy im Dashboard

## 10. Häufige Probleme

### "AI Learning Engine nicht verfügbar"
```bash
pip install requests textblob
python -m textblob.download_corpora
```

### "No API key for NewsAPI"
- Entweder Key in `.env` hinzufügen
- Oder `enable_news_learning: False` setzen

### "Model wird nicht besser"
- Warte mindestens 3-5 Retrainings (3-5 Tage)
- Prüfe ob genug News gesammelt werden
- Erhöhe `market_data_fetch_interval` für mehr Daten

### "Zu viele API-Anfragen"
```python
# Reduziere Sammel-Frequenz
DEFAULT_SETTINGS = {
    'news_fetch_interval_hours': 6,        # Weniger oft
    'market_data_fetch_interval_hours': 2,  # Weniger oft
}
```

## 11. Nächste Schritte

1. ✅ Bot läuft mit AI Learning
2. ⏳ 24h warten für erste Daten
3. 📊 Dashboard monitoren
4. 🎯 Nach 3-5 Tagen: Performance vergleichen
5. ⚙️ Parameter optimieren
6. 📈 Langzeit-Performance tracken

## 12. Dokumentation

- **Vollständige Docs**: `docs/AI_CONTINUOUS_LEARNING.md`
- **Architektur**: `CLAUDE.md` - Core architecture section
- **API Keys**: `docs/env.example.txt`
- **Config**: `trading_bot/config.py`

## Support

Fragen? Probleme?

1. Logs prüfen: `tail -f logs/trading_bot.log`
2. Dashboard starten: `python ai_learning_dashboard.py`
3. Datenbank checken: Siehe Abschnitt 6
4. Docs lesen: `docs/AI_CONTINUOUS_LEARNING.md`
5. Issue erstellen auf GitHub

---

**Viel Erfolg mit dem AI-powered Trading Bot! 🚀🧠**
