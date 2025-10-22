# 🧠 AI Continuous Learning System

## Überblick

Das AI Continuous Learning System sammelt automatisch Daten aus verschiedenen Quellen und trainiert das ML-Modell kontinuierlich nach, um immer präzisere Vorhersagen zu treffen.

### Datenquellen

1. **CoinDesk API** - Krypto-News und Marktanalysen
2. **NewsAPI** - Allgemeine Krypto-Nachrichten
3. **CryptoCompare** - News und Sentiment-Daten
4. **Kraken API** - Live-Marktdaten, Trades, OHLCV
5. **Eigene Trades** - P&L, Entry/Exit-Punkte

### Features

- ✅ **Automatische News-Sammlung** - Alle 4 Stunden
- ✅ **Marktdaten-Sammlung** - Jede Stunde
- ✅ **Sentiment-Analyse** - TextBlob + Keyword-basiert
- ✅ **Feature Engineering** - Technische Indikatoren + News-Sentiment
- ✅ **Auto-Retraining** - Alle 24 Stunden (konfigurierbar)
- ✅ **Performance-Tracking** - Accuracy-Historie in DB
- ✅ **Live-Dashboard** - Echtzeit-Monitoring des Lernfortschritts

## Konfiguration

### 1. API Keys einrichten

Erstelle eine `.env` Datei im Projekt-Root:

```bash
# Trading API
KRAKEN_API_KEY=your_kraken_key
KRAKEN_API_SECRET=your_kraken_secret

# News APIs (Optional aber empfohlen)
NEWSAPI_KEY=your_newsapi_key             # https://newsapi.org
CRYPTOCOMPARE_KEY=your_cryptocompare_key # https://min-api.cryptocompare.com
COINDESK_API_KEY=your_coindesk_key       # https://www.coindesk.com/api
```

### 2. Einstellungen in config.py

```python
DEFAULT_SETTINGS = {
    # ... andere Einstellungen ...

    # AI Learning
    'continuous_learning': True,           # Aktiviere Continuous Learning
    'enable_news_learning': True,          # News-basiertes Lernen
    'enable_market_learning': True,        # Marktdaten-basiertes Lernen

    # Sammlung-Intervalle
    'news_fetch_interval_hours': 4,        # News alle 4h
    'market_data_fetch_interval_hours': 1, # Marktdaten jede Stunde

    # Training
    'auto_retrain': True,                  # Automatisches Retraining
    'min_samples_retrain': 100,            # Min. Samples für Training
    'retrain_frequency_hours': 24,         # Retrain alle 24h
}
```

## Verwendung

### Starten mit AI Learning

```bash
# 1. Portfolio zurücksetzen
python helper_scripts/reset_portfolio.py

# 2. Bot mit AI Learning starten
python run_paper_trading.py

# Logs zeigen:
# ✓ AI Learning Engine initialisiert
# 🧠 AI Learning Engine gestartet (News + Marktdaten)
```

### Dashboard starten

```bash
# In neuem Terminal
python ai_learning_dashboard.py
```

Das Dashboard zeigt:
- 📊 Aktuelle Model-Accuracy
- 📚 Anzahl Training-Samples
- 📰 News & Sentiment (24h)
- 📈 Lernfortschritt (letzte 5 Trainings)
- ⚙️ System-Status

## Wie es funktioniert

### 1. Daten-Sammlung

Der AI Learning Engine läuft im Hintergrund als separater Thread:

```
┌─────────────────┐
│   Scheduler     │
│  (Background)   │
└────────┬────────┘
         │
         ├─► News Collection (alle 4h)
         │   ├─ CoinDesk API
         │   ├─ NewsAPI
         │   └─ CryptoCompare
         │
         ├─► Market Data (jede Stunde)
         │   ├─ OHLCV Daten (Kraken)
         │   ├─ Technische Indikatoren
         │   └─ Volume & Liquidität
         │
         └─► Auto-Retraining (alle 24h)
             ├─ Hole Training-Daten aus DB
             ├─ Feature Engineering
             ├─ Model Training
             └─ Performance-Tracking
```

### 2. Feature Engineering

Für jedes Training-Sample werden folgende Features erstellt:

**Technische Indikatoren:**
- SMA (20, 50, 200)
- EMA (9, 21, 50)
- RSI (14)
- MACD
- Bollinger Bands
- ATR
- Volume-Indikatoren

**News-Features:**
- Sentiment-Score (-1 bis +1)
- Sentiment-Label (positive/neutral/negative)
- News-Volumen (Anzahl Artikel)

**Kombinierte Features:**
- Preis + Sentiment-Korrelation
- Trend-Stärke + News-Bias
- Volatilität + News-Aktivität

### 3. Label-Generierung

Labels werden automatisch aus Marktdaten erstellt:

```python
# Preis in 1h höher/niedriger?
future_return = close.pct_change(1).shift(-1)

if future_return > 0.001:   # >0.1% Up
    label = 2  # BUY
elif future_return < -0.001: # >-0.1% Down
    label = 0  # SELL
else:
    label = 1  # HOLD
```

### 4. Training-Pipeline

```python
# 1. Sammle Daten
training_samples = db.get_training_data(limit=10000)

# 2. Extrahiere Features & Labels
X, y = extract_features_and_labels(training_samples)

# 3. Trainiere Modell
model.train(X, y)

# 4. Evaluiere
accuracy = evaluate(model, X_test, y_test)

# 5. Speichere Performance
db.save_model_performance({
    'accuracy': accuracy,
    'samples_used': len(X),
    'timestamp': now()
})

# 6. Speichere neues Modell
model.save('models/trading_model.pkl')
```

## Datenbank-Schema

### Training Data
```sql
CREATE TABLE training_data (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    symbol TEXT,
    features TEXT,  -- JSON mit allen Features
    label INTEGER,  -- 0=SELL, 1=HOLD, 2=BUY
    pnl REAL,       -- Actual P&L (für Evaluation)
    timestamp TEXT
);
```

### News
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    title TEXT,
    content TEXT,
    source TEXT,
    url TEXT,
    sentiment_score REAL,
    sentiment_label TEXT,
    published_at TEXT
);
```

### Model Performance
```sql
CREATE TABLE model_performance (
    id INTEGER PRIMARY KEY,
    model_version TEXT,
    accuracy REAL,
    precision_score REAL,
    recall REAL,
    f1_score REAL,
    samples_count INTEGER,
    training_duration REAL,
    timestamp TEXT
);
```

## Monitoring & Debugging

### Logs checken

```bash
# Live-Logs
tail -f logs/trading_bot.log | grep -E "(Learning|News|Training)"

# Nur Learning-Events
grep "AI Learning" logs/trading_bot.log
```

### Datenbank-Checks

```bash
# Training-Daten prüfen
python -c "
from trading_bot.database import get_database
db = get_database()
df = db.get_training_data(limit=1000)
print(f'Training Samples: {len(df)}')
print(f'Labels: {df[\"label\"].value_counts()}')
"

# News prüfen
python -c "
from trading_bot.database import get_database
db = get_database()
news = db.get_recent_news('BTC', hours=24)
print(f'News (24h): {len(news)}')
sentiments = [n['sentiment_score'] for n in news]
print(f'Ø Sentiment: {sum(sentiments)/len(sentiments):.2f}')
"

# Performance-Historie
python -c "
from trading_bot.database import get_database
db = get_database()
perf = db.get_model_performance_history(limit=10)
for p in perf:
    print(f\"{p['timestamp'][:16]} - Accuracy: {p['accuracy']*100:.1f}%\")
"
```

### Dashboard

Das AI Learning Dashboard (`ai_learning_dashboard.py`) zeigt:

1. **Model Performance**
   - Aktuelle Accuracy
   - Training Samples
   - Letztes Training
   - Trend (Verbesserung/Verschlechterung)

2. **Training Daten**
   - Total Samples
   - Label-Verteilung (Sell/Hold/Buy)

3. **News & Sentiment**
   - News-Volumen (24h)
   - Durchschnittliches Sentiment
   - Positiv/Neutral/Negativ-Verteilung

4. **Lernfortschritt**
   - Letzte 5 Trainings
   - Accuracy-Entwicklung
   - Samples pro Training

5. **System Status**
   - Bot-Status (Aktiv/Inaktiv)
   - Datenbank-Größe

## Performance-Optimierung

### Zu wenig Training-Daten?

```python
# Reduziere min_samples_retrain
DEFAULT_SETTINGS = {
    'min_samples_retrain': 50,  # Statt 100
}

# Oder sammle häufiger Marktdaten
DEFAULT_SETTINGS = {
    'market_data_fetch_interval_hours': 0.5,  # Alle 30 Min
}
```

### Modell verbessert sich nicht?

1. **Prüfe News-Qualität**
   ```bash
   # Sentiment-Verteilung prüfen
   python -c "from trading_bot.database import get_database; ..."
   ```

2. **Feature-Korrelation**
   ```python
   # In Python-Shell
   import pandas as pd
   from trading_bot.database import get_database

   db = get_database()
   df = db.get_training_data(limit=1000)

   # Korrelation mit Labels
   df.corr()['label'].sort_values()
   ```

3. **Mehr Datenquellen**
   - Füge weitere News-APIs hinzu
   - Sammle Social Media Sentiment (Twitter)
   - On-Chain Daten (Glassnode)

### Speicherplatz sparen

```python
# In database.py
def cleanup_old_training_data(days=30):
    """Lösche alte Training-Daten"""
    cursor = self.conn.cursor()
    cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
    cursor.execute("DELETE FROM training_data WHERE timestamp < ?", (cutoff,))
    self.conn.commit()
```

## API-Limits beachten

### NewsAPI (Free Tier)
- 100 Requests/Tag
- Max. 100 Artikel pro Request
- **Lösung**: Sammle alle 4h statt jede Stunde

### CoinDesk
- Unbegrenzt für öffentliche API
- Rate Limit: ~60 Requests/Minute

### CryptoCompare
- 100,000 Requests/Monat (Free)
- **Lösung**: Cache News in DB

## Erweiterte Features (Optional)

### 1. Multi-Asset Learning

```python
# Sammle Daten für mehrere Coins
symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'BNB/USD']

for symbol in symbols:
    engine._collect_market_data_for_symbol(symbol)
```

### 2. Transfer Learning

```python
# Nutze vortrainiertes Modell
from transformers import AutoModelForSequenceClassification

sentiment_model = AutoModelForSequenceClassification.from_pretrained(
    "finbert-sentiment"  # Speziell für Finanznachrichten
)
```

### 3. Reinforcement Learning

```python
# RL Agent lernt aus Trades
from trader.sizing.rl_sizer import RLSizer

rl_agent = RLSizer(
    action_space=3,  # SELL, HOLD, BUY
    state_size=50    # Features
)
```

## Troubleshooting

### "AI Learning Engine nicht verfügbar"

```bash
# Installiere fehlende Dependencies
pip install requests textblob

# Prüfe Import
python -c "from trading_bot.ai_learning_engine import AILearningEngine"
```

### "No module named 'textblob'"

```bash
pip install textblob
python -m textblob.download_corpora
```

### "News-Sammlung schlägt fehl"

1. Prüfe API Keys in `.env`
2. Teste CoinDesk manuell:
   ```python
   from trading_bot.ai_learning_engine import CoinDeskAPI
   api = CoinDeskAPI()
   news = api.get_crypto_news(limit=5)
   print(news)
   ```

### "Modell wird nicht besser"

1. **Mehr Daten sammeln** (min. 1000 Samples)
2. **Feature Engineering verbessern**
3. **Hyperparameter tunen**
4. **Label-Strategie anpassen** (z.B. 0.5% statt 0.1%)

## Best Practices

1. ✅ **Regelmäßig Backups** der Datenbank erstellen
2. ✅ **Logs überwachen** auf Fehler
3. ✅ **Dashboard nutzen** für Lernfortschritt
4. ✅ **Performance tracken** (Accuracy-Trend)
5. ✅ **API-Limits beachten** (News-Sammlung throtteln)
6. ✅ **Features evaluieren** (Korrelation mit Labels)
7. ✅ **Alte Daten löschen** (>90 Tage)

## Nächste Schritte

1. Bot mit AI Learning starten
2. 24h laufen lassen für erste Daten
3. Dashboard monitoren
4. Nach erstem Retraining: Performance prüfen
5. Gegebenenfalls Parameter anpassen
6. Langzeit-Performance tracken (Wochen/Monate)

## Support

Bei Problemen:
1. Logs prüfen (`logs/trading_bot.log`)
2. Dashboard starten (`python ai_learning_dashboard.py`)
3. Datenbank checken (siehe "Monitoring & Debugging")
4. Issue erstellen auf GitHub
