# 🧠 Wie du der KI Wissen beibringen kannst

## Übersicht

Es gibt **5 Hauptwege**, um der KI Wissen beizubringen:

1. **📊 Training-Daten** - Historische Trades mit Labels
2. **📚 Strategien** - Vordefinierte Handelsstrategien
3. **🎯 Feature Engineering** - Neue Indikatoren hinzufügen
4. **📖 Knowledge Base** - Textdokumente, PDFs, Trading-Bücher
5. **🔄 Reinforcement Learning** - Lernen durch Belohnungen

---

## 1. 📊 Training-Daten hinzufügen

### A) Automatische Daten-Sammlung (läuft bereits)

Das AI Learning System sammelt automatisch:
- ✅ News-Artikel mit Sentiment
- ✅ Marktdaten (OHLCV, Indikatoren)
- ✅ Trades und deren Ergebnisse

### B) Manuell Training-Daten hinzufügen

Erstelle ein Script, um eigenes Wissen hinzuzufügen:

```python
# helper_scripts/add_training_knowledge.py
from trading_bot.database import get_database
from datetime import datetime, UTC
import json

db = get_database()

# Beispiel: "Bei RSI < 30 und positiven News → BUY"
training_sample = {
    'symbol': 'BTC/USD',
    'timestamp': datetime.now(UTC).isoformat(),
    'features': json.dumps({
        'rsi': 28.5,           # Überverkauft
        'macd': -50,           # Negativ
        'sma_20': 67000,
        'sma_50': 68000,
        'volume': 1500000,
        'news_sentiment': 0.7,  # Positiv!
        'volatility': 0.02
    }),
    'label': 2,  # 2 = BUY (0=SELL, 1=HOLD, 2=BUY)
    'future_return': 0.025,  # +2.5% Gewinn erwartet
    'news_sentiment': 0.7
}

db.save_training_data(training_sample)
print("✓ Training-Sample hinzugefügt")
```

**Viele Samples auf einmal hinzufügen:**

```python
# Strategie: "Mean Reversion bei Überverkauf"
samples = [
    # RSI < 30 + Positive News = BUY
    {'features': {'rsi': 25, 'news_sentiment': 0.6, ...}, 'label': 2, 'future_return': 0.03},
    {'features': {'rsi': 28, 'news_sentiment': 0.5, ...}, 'label': 2, 'future_return': 0.02},

    # RSI > 70 + Negative News = SELL
    {'features': {'rsi': 75, 'news_sentiment': -0.6, ...}, 'label': 0, 'future_return': -0.03},
    {'features': {'rsi': 78, 'news_sentiment': -0.5, ...}, 'label': 0, 'future_return': -0.02},

    # Neutral = HOLD
    {'features': {'rsi': 50, 'news_sentiment': 0.0, ...}, 'label': 1, 'future_return': 0.0},
]

for sample in samples:
    sample['symbol'] = 'BTC/USD'
    sample['timestamp'] = datetime.now(UTC).isoformat()
    sample['features'] = json.dumps(sample['features'])
    db.save_training_data(sample)

print(f"✓ {len(samples)} Training-Samples hinzugefügt")
```

---

## 2. 📚 Strategien hinzufügen

### A) In der Konfiguration

Bearbeite `trading_bot/config.py`:

```python
STRATEGIES = {
    # Bestehende Strategien...

    # NEUE STRATEGIE: Accumulation Zone
    'accumulation_zone': {
        'enabled': True,
        'description': 'Kaufe bei niedrigen Preisen und hohem Volumen',
        'rules': {
            # Preis ist 10% unter SMA-200
            'price_below_sma200': -0.10,

            # Volumen ist 2x über Durchschnitt
            'volume_multiplier': 2.0,

            # RSI zwischen 20-40 (überverkauft aber nicht extrem)
            'rsi_range': [20, 40],

            # MACD zeigt Aufwärtstrend
            'macd_positive_cross': True
        },
        'position_size': 0.15,  # 15% des Portfolios
        'stop_loss_pct': 0.05,  # 5% Stop-Loss
        'take_profit_pct': 0.20 # 20% Take-Profit
    },

    # NEUE STRATEGIE: News-Driven Trading
    'news_momentum': {
        'enabled': True,
        'description': 'Handel basierend auf News-Sentiment',
        'rules': {
            # Sehr positives Sentiment (>0.7)
            'min_news_sentiment': 0.7,

            # Viele News in letzten 4h (>10 Artikel)
            'min_news_count_4h': 10,

            # Preis steigt bereits (+2%)
            'min_price_change_1h': 0.02,

            # Bestätigung durch Volumen
            'volume_surge': 1.5
        },
        'position_size': 0.10,
        'stop_loss_pct': 0.03,
        'take_profit_pct': 0.08
    }
}
```

### B) Eigene Strategie-Klasse erstellen

Erstelle `trading_bot/strategies/my_strategy.py`:

```python
"""
Meine eigene Trading-Strategie basierend auf Wyckoff-Methode
"""
from typing import Dict, Optional
import pandas as pd
import numpy as np

class WyckoffAccumulation:
    """
    Wyckoff Accumulation Strategie:
    - Identifiziert Akkumulationszonen
    - Sucht nach Spring (Fake-Breakout nach unten)
    - Kauft bei Sign of Strength (SOS)
    """

    def __init__(self, config: Dict):
        self.config = config
        self.name = "wyckoff_accumulation"

    def analyze(self, df: pd.DataFrame, news_sentiment: float = 0.0) -> Optional[Dict]:
        """
        Analysiert Marktdaten nach Wyckoff-Prinzipien

        Returns:
            Signal-Dict oder None
        """
        if len(df) < 100:
            return None

        current = df.iloc[-1]
        prev = df.iloc[-2]

        # 1. Identifiziere Trading Range (Accumulation)
        high_20 = df['high'].rolling(20).max().iloc[-1]
        low_20 = df['low'].rolling(20).min().iloc[-1]
        range_pct = (high_20 - low_20) / low_20

        # Trading Range sollte eng sein (<5%)
        if range_pct > 0.05:
            return None

        # 2. Suche nach Spring (Fake-Breakout)
        # Preis bricht unter Support, aber schließt darüber
        support = low_20
        spring_detected = (
            current['low'] < support * 0.99 and  # Bricht unter Support
            current['close'] > support * 1.01    # Schließt aber darüber
        )

        # 3. Sign of Strength (SOS)
        # Starker Aufwärtsmove mit hohem Volumen
        price_increase = (current['close'] - prev['close']) / prev['close']
        volume_surge = current['volume'] / df['volume'].rolling(20).mean().iloc[-1]

        sos_detected = (
            price_increase > 0.02 and  # +2% Anstieg
            volume_surge > 1.5         # 1.5x normales Volumen
        )

        # 4. Signal generieren
        if spring_detected and sos_detected:
            return {
                'action': 'buy',
                'confidence': 0.85,
                'strategy': self.name,
                'reason': 'Wyckoff Spring + Sign of Strength detected',
                'stop_loss': support * 0.97,  # 3% unter Support
                'take_profit': current['close'] * 1.15,  # 15% Target
                'position_size': 0.20  # 20% Portfolio
            }

        return None
```

Dann registriere sie im Bot:

```python
# In bot.py bei _initialize_components()
from trading_bot.strategies.my_strategy import WyckoffAccumulation

self.custom_strategies = [
    WyckoffAccumulation(config=self.config)
]
```

---

## 3. 🎯 Feature Engineering - Neue Indikatoren

Füge Indikatoren hinzu, die deine Trading-Philosophie widerspiegeln:

```python
# trading_bot/indicators.py - Erweitern

def calculate_wyckoff_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Wyckoff-spezifische Indikatoren
    """
    # Volume Spread Analysis (VSA)
    df['spread'] = df['high'] - df['low']
    df['spread_avg'] = df['spread'].rolling(20).mean()
    df['spread_ratio'] = df['spread'] / df['spread_avg']

    # Volume Climax
    df['volume_avg'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_avg']
    df['climax'] = (df['volume_ratio'] > 2.0).astype(int)

    # Effort vs Result
    # Wenn Volumen hoch aber Spread klein → Akkumulation
    df['effort_result'] = df['volume_ratio'] / (df['spread_ratio'] + 0.1)

    # Supply & Demand Zones
    df['supply_zone'] = df['high'].rolling(50).max()
    df['demand_zone'] = df['low'].rolling(50).min()

    return df

def calculate_smart_money_flow(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Smart Money Concepts (SMC)
    """
    # Order Blocks (letzte Kerze vor starkem Move)
    df['price_change'] = df['close'].pct_change()
    df['strong_move'] = (abs(df['price_change']) > 0.03).astype(int)

    # Bullish Order Block: Letzte bearish Kerze vor bullish Move
    df['order_block_bull'] = (
        (df['close'] < df['open']) &  # Bearish Kerze
        (df['strong_move'].shift(-1) == 1) &  # Gefolgt von starkem Move
        (df['price_change'].shift(-1) > 0)  # Bullish Move
    ).astype(int)

    # Fair Value Gap (Inefficiency)
    df['fvg_bullish'] = (
        df['low'].shift(-1) > df['high'].shift(1)
    ).astype(int)

    df['fvg_bearish'] = (
        df['high'].shift(-1) < df['low'].shift(1)
    ).astype(int)

    return df
```

---

## 4. 📖 Knowledge Base - Textdokumente einlesen

### Erstelle ein Knowledge-System

```python
# trading_bot/knowledge_base.py
"""
Knowledge Base System - Lernt aus Textdokumenten
"""
import json
import re
from pathlib import Path
from typing import List, Dict

class TradingKnowledgeBase:
    """
    Liest Trading-Wissen aus Textdateien, PDFs, etc.
    Extrahiert Regeln und Strategien
    """

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        self.rules = []
        self.strategies = []

    def load_from_text(self, filepath: str):
        """
        Liest Trading-Regeln aus Text-Datei

        Format:
        REGEL: Wenn RSI < 30 und Volumen > Durchschnitt → BUY
        REGEL: Wenn MACD kreuzt nach oben → BUY Signal
        STRATEGIE: Mean Reversion bei RSI < 25
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extrahiere Regeln
        rules = re.findall(r'REGEL:\s*(.+?)(?:\n|$)', content)
        self.rules.extend(rules)

        # Extrahiere Strategien
        strategies = re.findall(r'STRATEGIE:\s*(.+?)(?:\n|$)', content)
        self.strategies.extend(strategies)

        print(f"✓ {len(rules)} Regeln und {len(strategies)} Strategien geladen")

    def parse_rule_to_training_sample(self, rule_text: str) -> Dict:
        """
        Konvertiert Text-Regel zu Training-Sample

        "Wenn RSI < 30 und Volumen hoch → BUY"
        →
        {'features': {'rsi': 25, 'volume_ratio': 1.8}, 'label': 2}
        """
        # Einfaches NLP-Parsing
        rule_lower = rule_text.lower()

        features = {}
        label = None

        # RSI-Werte extrahieren
        rsi_match = re.search(r'rsi\s*<\s*(\d+)', rule_lower)
        if rsi_match:
            features['rsi'] = float(rsi_match.group(1)) - 5  # Beispielwert

        rsi_match_gt = re.search(r'rsi\s*>\s*(\d+)', rule_lower)
        if rsi_match_gt:
            features['rsi'] = float(rsi_match_gt.group(1)) + 5

        # Volumen
        if 'volumen > durchschnitt' in rule_lower or 'volumen hoch' in rule_lower:
            features['volume_ratio'] = 1.8

        # MACD
        if 'macd' in rule_lower:
            if 'nach oben' in rule_lower or 'positiv' in rule_lower:
                features['macd'] = 20
            elif 'nach unten' in rule_lower or 'negativ' in rule_lower:
                features['macd'] = -20

        # Label bestimmen
        if 'buy' in rule_lower or 'kaufen' in rule_lower:
            label = 2
        elif 'sell' in rule_lower or 'verkaufen' in rule_lower:
            label = 0
        elif 'hold' in rule_lower or 'halten' in rule_lower:
            label = 1

        return {
            'features': features,
            'label': label,
            'source': 'knowledge_base',
            'rule_text': rule_text
        }

    def export_to_training_data(self, db):
        """
        Konvertiert Knowledge Base zu Training-Daten
        """
        from datetime import datetime, UTC
        import json

        for rule in self.rules:
            sample = self.parse_rule_to_training_sample(rule)

            if sample['label'] is not None:
                db.save_training_data({
                    'symbol': 'BTC/USD',
                    'timestamp': datetime.now(UTC).isoformat(),
                    'features': json.dumps(sample['features']),
                    'label': sample['label'],
                    'future_return': 0.02 if sample['label'] == 2 else -0.02,
                    'news_sentiment': 0.0
                })

        print(f"✓ {len(self.rules)} Regeln zu Training-Daten konvertiert")
```

### Verwendung:

```python
# helper_scripts/import_knowledge.py
from trading_bot.knowledge_base import TradingKnowledgeBase
from trading_bot.database import get_database

# Erstelle Knowledge Base
kb = TradingKnowledgeBase()

# Lade Wissen aus Datei
kb.load_from_text('knowledge/my_trading_rules.txt')

# Exportiere zu Training-Daten
db = get_database()
kb.export_to_training_data(db)

print("✓ Wissen erfolgreich importiert!")
```

Erstelle `knowledge/my_trading_rules.txt`:

```
REGEL: Wenn RSI < 30 und Volumen > Durchschnitt → BUY
REGEL: Wenn RSI > 70 und Volumen hoch → SELL
REGEL: Wenn MACD kreuzt nach oben und RSI < 50 → BUY
REGEL: Wenn Preis unter SMA-200 und News negativ → SELL
REGEL: Wenn Preis über SMA-50 und MACD positiv → HOLD

STRATEGIE: Mean Reversion bei RSI < 25
STRATEGIE: Breakout bei Volumen > 2x Durchschnitt
STRATEGIE: News-Momentum bei Sentiment > 0.7
```

---

## 5. 🔄 Reinforcement Learning (Fortgeschritten)

Lasse die KI durch Belohnungen lernen:

```python
# trading_bot/reinforcement_learning.py
"""
Reinforcement Learning Agent
Lernt durch Belohnungen (Profit/Loss)
"""
import numpy as np
from collections import deque

class QLearningTrader:
    """
    Q-Learning Agent für Trading
    """

    def __init__(self, state_size: int, action_size: int = 3):
        self.state_size = state_size
        self.action_size = action_size  # 0=SELL, 1=HOLD, 2=BUY

        # Q-Table: State → Action → Reward
        self.q_table = {}

        # Hyperparameter
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate

        # Erfahrungs-Speicher
        self.memory = deque(maxlen=10000)

    def get_action(self, state: np.ndarray) -> int:
        """
        Wählt Aktion basierend auf Q-Table
        """
        state_key = self._discretize_state(state)

        # Exploration vs Exploitation
        if np.random.random() < self.epsilon:
            return np.random.randint(0, self.action_size)  # Zufällig

        # Beste Aktion wählen
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)

        return np.argmax(self.q_table[state_key])

    def learn(self, state, action, reward, next_state, done):
        """
        Q-Learning Update
        """
        state_key = self._discretize_state(state)
        next_state_key = self._discretize_state(next_state)

        # Init Q-Values
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)

        # Q-Learning Formula
        current_q = self.q_table[state_key][action]
        max_next_q = np.max(self.q_table[next_state_key])

        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[state_key][action] = new_q

        # Speichere Erfahrung
        self.memory.append((state, action, reward, next_state, done))

    def _discretize_state(self, state: np.ndarray) -> tuple:
        """
        Konvertiert kontinuierlichen State zu diskretem Key
        """
        # Binning für kontinuierliche Werte
        bins = 10
        discretized = tuple(
            int((val - val.min()) / (val.max() - val.min() + 1e-8) * bins)
            for val in state
        )
        return discretized
```

Integration in den Bot:

```python
# In bot.py
from trading_bot.reinforcement_learning import QLearningTrader

# Bei __init__
self.rl_agent = QLearningTrader(state_size=20)

# Nach jedem Trade
def _update_rl_agent(self, trade: Dict, profit: float):
    """Trainiert RL-Agent mit Trade-Ergebnis"""
    # State = Features zum Zeitpunkt des Trades
    # Reward = Profit/Loss
    reward = profit  # +1.5% = +0.015

    self.rl_agent.learn(
        state=trade['features'],
        action=trade['action'],  # 0/1/2
        reward=reward,
        next_state=current_features,
        done=True
    )
```

---

## 📋 Zusammenfassung - Schnelle Aktionen

### Sofort umsetzbar:

```bash
# 1. Strategie in config.py hinzufügen
nano trading_bot/config.py  # Neue Strategie unter STRATEGIES

# 2. Training-Samples hinzufügen
python -c "
from trading_bot.database import get_database
import json
from datetime import datetime, UTC

db = get_database()
db.save_training_data({
    'symbol': 'BTC/USD',
    'timestamp': datetime.now(UTC).isoformat(),
    'features': json.dumps({'rsi': 28, 'news_sentiment': 0.6, 'volume_ratio': 1.5}),
    'label': 2,  # BUY
    'future_return': 0.03
})
print('✓ Training-Sample hinzugefügt')
"

# 3. Bot neu trainieren (bei genug Samples)
# Automatisch alle 24h oder manuell triggern
```

### Fortgeschritten:

1. **Eigene Strategie-Klasse** erstellen (`my_strategy.py`)
2. **Knowledge Base** mit Text-Dateien füttern
3. **Neue Indikatoren** in `indicators.py` implementieren
4. **Reinforcement Learning** aktivieren

---

## 🎯 Best Practices

1. ✅ **Start klein**: Füge 50-100 Training-Samples hinzu
2. ✅ **Konsistenz**: Verwende einheitliche Feature-Namen
3. ✅ **Validierung**: Teste neue Strategien im Paper-Trading
4. ✅ **Dokumentation**: Schreibe auf, warum bestimmte Regeln funktionieren
5. ✅ **Iteration**: Überwache Accuracy und passe an

---

## 📚 Weitere Ressourcen

- `AI_CONTINUOUS_LEARNING.md` - Auto-Learning System
- `trading_bot/config.py` - Strategien konfigurieren
- `trading_bot/indicators.py` - Neue Indikatoren
- `helper_scripts/` - Utility-Scripts

---

**Die KI lernt am besten durch eine Kombination aus:**
1. 📊 Echten Trading-Daten (automatisch)
2. 📚 Deinem Wissen (manuell hinzugefügt)
3. 🎯 Strategischen Regeln (konfiguriert)
4. 🔄 Erfahrung (Reinforcement Learning)

**Viel Erfolg beim Trainieren! 🚀**
