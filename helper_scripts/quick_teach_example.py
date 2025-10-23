"""
Schnelles Beispiel: Der KI Strategie-Wissen beibringen
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_bot.database import get_database
from datetime import datetime
import json

# UTC import
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


def teach_mean_reversion_strategy():
    """
    Bringt der KI die Mean Reversion Strategie bei:
    - Bei RSI < 30 (überverkauft) → BUY
    - Bei RSI > 70 (überkauft) → SELL
    - Bei RSI 40-60 (neutral) → HOLD
    """
    print("\n" + "=" * 70)
    print("🧠 TRAINIERE KI: Mean Reversion Strategie")
    print("=" * 70)

    db = get_database()

    # Strategie-Samples
    samples = [
        # ===== ÜBERVERKAUFT → BUY =====
        {
            'desc': 'Stark überverkauft + positives Sentiment',
            'features': {
                'rsi': 22,
                'macd': -30,
                'sma_20': 67000,
                'price': 65500,  # 2.2% unter SMA
                'volume_ratio': 1.3,
                'news_sentiment': 0.4
            },
            'label': 2,  # BUY
            'expected_return': 0.04  # +4%
        },
        {
            'desc': 'Überverkauft + hohe Volumen',
            'features': {
                'rsi': 28,
                'macd': -20,
                'sma_20': 67000,
                'price': 66000,
                'volume_ratio': 1.8,
                'news_sentiment': 0.2
            },
            'label': 2,  # BUY
            'expected_return': 0.03
        },

        # ===== ÜBERKAUFT → SELL =====
        {
            'desc': 'Stark überkauft + negatives Sentiment',
            'features': {
                'rsi': 78,
                'macd': 30,
                'sma_20': 67000,
                'price': 69500,  # 3.7% über SMA
                'volume_ratio': 1.2,
                'news_sentiment': -0.5
            },
            'label': 0,  # SELL
            'expected_return': -0.04
        },
        {
            'desc': 'Überkauft + schwaches Volumen',
            'features': {
                'rsi': 72,
                'macd': 25,
                'sma_20': 67000,
                'price': 68500,
                'volume_ratio': 0.8,
                'news_sentiment': -0.2
            },
            'label': 0,  # SELL
            'expected_return': -0.03
        },

        # ===== NEUTRAL → HOLD =====
        {
            'desc': 'RSI neutral, warte auf besseren Entry',
            'features': {
                'rsi': 50,
                'macd': 0,
                'sma_20': 67000,
                'price': 67000,
                'volume_ratio': 1.0,
                'news_sentiment': 0.0
            },
            'label': 1,  # HOLD
            'expected_return': 0.005
        },
        {
            'desc': 'Leicht bullish aber noch nicht stark genug',
            'features': {
                'rsi': 45,
                'macd': -10,
                'sma_20': 67000,
                'price': 66500,
                'volume_ratio': 1.1,
                'news_sentiment': 0.1
            },
            'label': 1,  # HOLD
            'expected_return': 0.01
        },

        # ===== EDGE CASES =====
        {
            'desc': 'Divergence: RSI niedrig aber negative News → Vorsichtig HOLD',
            'features': {
                'rsi': 32,
                'macd': -15,
                'sma_20': 67000,
                'price': 66000,
                'volume_ratio': 0.7,  # Schwaches Volumen!
                'news_sentiment': -0.6  # Sehr negative News!
            },
            'label': 1,  # HOLD (nicht kaufen trotz niedrigem RSI)
            'expected_return': -0.02
        },
        {
            'desc': 'Divergence: RSI hoch aber sehr positive News → Noch halten',
            'features': {
                'rsi': 68,
                'macd': 20,
                'sma_20': 67000,
                'price': 68000,
                'volume_ratio': 2.5,  # Hohes Volumen
                'news_sentiment': 0.8  # Sehr positive News
            },
            'label': 1,  # HOLD (Momentum könnte weitergehen)
            'expected_return': 0.02
        },
    ]

    # Speichere Samples
    for i, sample in enumerate(samples, 1):
        label_str = ['SELL', 'HOLD', 'BUY'][sample['label']]

        db.save_training_data({
            'symbol': 'BTC/USD',
            'timestamp': datetime.now(UTC).isoformat(),
            'features': json.dumps(sample['features']),
            'label': sample['label'],
            'future_return': sample['expected_return'],
            'news_sentiment': sample['features']['news_sentiment']
        })

        print(f"{i}. ✓ {sample['desc']}")
        print(f"   Aktion: {label_str} | Return: {sample['expected_return']*100:+.1f}%")
        print(f"   RSI: {sample['features']['rsi']} | Sentiment: {sample['features']['news_sentiment']:+.1f}")
        print()

    db.close()

    print("=" * 70)
    print(f"✅ {len(samples)} Training-Samples erfolgreich hinzugefügt!")
    print("=" * 70)
    print("\n📊 Nächste Schritte:")
    print("1. Weitere Samples hinzufügen mit: python helper_scripts/teach_ai.py")
    print("2. Bei 100+ Samples: Bot trainiert automatisch neu")
    print("3. Dashboard ansehen: python ai_learning_dashboard.py")
    print()


if __name__ == "__main__":
    teach_mean_reversion_strategy()
