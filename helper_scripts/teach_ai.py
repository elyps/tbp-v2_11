"""
Teach AI - Einfaches Tool um der KI Wissen beizubringen
Verwendung: python helper_scripts/teach_ai.py
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


def show_menu():
    """Zeigt das Hauptmenü."""
    print("\n" + "=" * 70)
    print("🧠 KI TRAINIEREN - Wissen hinzufügen")
    print("=" * 70)
    print("\n1. Training-Sample hinzufügen (Einzeln)")
    print("2. Strategie-Regel hinzufügen (Batch)")
    print("3. Zeige aktuelle Training-Daten")
    print("4. Importiere aus Text-Datei")
    print("5. Beenden")
    print()


def add_single_sample(db):
    """Fügt ein einzelnes Training-Sample hinzu."""
    print("\n--- TRAINING-SAMPLE HINZUFÜGEN ---\n")

    # Symbol
    symbol = input("Symbol (z.B. BTC/USD, ETH/USD) [BTC/USD]: ").strip() or "BTC/USD"

    # Features sammeln
    print("\n📊 Technische Indikatoren:")
    features = {}

    # RSI
    rsi = input("  RSI (0-100) [50]: ").strip()
    features['rsi'] = float(rsi) if rsi else 50.0

    # MACD
    macd = input("  MACD (-100 bis +100) [0]: ").strip()
    features['macd'] = float(macd) if macd else 0.0

    # SMA Position
    price_vs_sma = input("  Preis vs SMA-50 in % (z.B. +5 = 5% darüber) [0]: ").strip()
    features['price_vs_sma50'] = float(price_vs_sma) if price_vs_sma else 0.0

    # Volumen
    volume_ratio = input("  Volumen-Ratio (1.0 = Normal, 2.0 = Doppelt) [1.0]: ").strip()
    features['volume_ratio'] = float(volume_ratio) if volume_ratio else 1.0

    # News Sentiment
    print("\n📰 News & Sentiment:")
    news_sentiment = input("  News-Sentiment (-1 bis +1, 0=neutral) [0]: ").strip()
    features['news_sentiment'] = float(news_sentiment) if news_sentiment else 0.0

    # Label
    print("\n🎯 Erwartete Aktion:")
    print("  0 = SELL (Verkaufen)")
    print("  1 = HOLD (Halten)")
    print("  2 = BUY (Kaufen)")
    label = input("Label (0/1/2): ").strip()

    if label not in ['0', '1', '2']:
        print("❌ Ungültiges Label!")
        return

    label = int(label)

    # Erwartete Rendite
    future_return = input("\nErwartete Rendite in % (z.B. +3 = +3%) [0]: ").strip()
    future_return = float(future_return) / 100 if future_return else 0.0

    # Sample erstellen
    sample = {
        'symbol': symbol,
        'timestamp': datetime.now(UTC).isoformat(),
        'features': json.dumps(features),
        'label': label,
        'future_return': future_return,
        'news_sentiment': features['news_sentiment']
    }

    # Speichern
    db.save_training_data(sample)

    print(f"\n✅ Training-Sample gespeichert!")
    print(f"   Symbol: {symbol}")
    print(f"   Label: {'SELL' if label == 0 else 'HOLD' if label == 1 else 'BUY'}")
    print(f"   Features: {features}")


def add_strategy_batch(db):
    """Fügt mehrere Samples basierend auf einer Strategie hinzu."""
    print("\n--- STRATEGIE-REGELN HINZUFÜGEN ---\n")

    print("Wähle Strategie:")
    print("1. Mean Reversion (RSI-basiert)")
    print("2. Momentum Trading (Trend)")
    print("3. Breakout (Volumen)")
    print("4. News-Sentiment Trading")

    choice = input("\nStrategie (1-4): ").strip()

    samples = []

    if choice == '1':
        # Mean Reversion
        print("\n📊 Mean Reversion Strategie:")
        print("   - RSI < 30 → BUY")
        print("   - RSI > 70 → SELL")
        print("   - RSI 40-60 → HOLD")

        samples = [
            # Überverkauft → BUY
            {'rsi': 25, 'macd': -20, 'label': 2, 'return': 0.03},
            {'rsi': 28, 'macd': -15, 'label': 2, 'return': 0.025},
            {'rsi': 22, 'macd': -25, 'label': 2, 'return': 0.035},

            # Überkauft → SELL
            {'rsi': 75, 'macd': 20, 'label': 0, 'return': -0.03},
            {'rsi': 78, 'macd': 15, 'label': 0, 'return': -0.025},
            {'rsi': 72, 'macd': 25, 'label': 0, 'return': -0.035},

            # Neutral → HOLD
            {'rsi': 50, 'macd': 0, 'label': 1, 'return': 0.005},
            {'rsi': 45, 'macd': -5, 'label': 1, 'return': 0.002},
            {'rsi': 55, 'macd': 5, 'label': 1, 'return': 0.003},
        ]

    elif choice == '2':
        # Momentum
        print("\n📈 Momentum Strategie:")
        print("   - MACD > 0 + Preis > SMA → BUY")
        print("   - MACD < 0 + Preis < SMA → SELL")

        samples = [
            # Aufwärtstrend → BUY
            {'rsi': 60, 'macd': 30, 'price_vs_sma50': 5, 'label': 2, 'return': 0.04},
            {'rsi': 65, 'macd': 25, 'price_vs_sma50': 8, 'label': 2, 'return': 0.05},

            # Abwärtstrend → SELL
            {'rsi': 40, 'macd': -30, 'price_vs_sma50': -5, 'label': 0, 'return': -0.04},
            {'rsi': 35, 'macd': -25, 'price_vs_sma50': -8, 'label': 0, 'return': -0.05},
        ]

    elif choice == '3':
        # Breakout
        print("\n🚀 Breakout Strategie:")
        print("   - Volumen > 2x + Preis steigt → BUY")

        samples = [
            # Bullish Breakout
            {'rsi': 55, 'volume_ratio': 2.5, 'price_vs_sma50': 3, 'label': 2, 'return': 0.06},
            {'rsi': 58, 'volume_ratio': 3.0, 'price_vs_sma50': 5, 'label': 2, 'return': 0.08},

            # Bearish Breakout
            {'rsi': 45, 'volume_ratio': 2.5, 'price_vs_sma50': -3, 'label': 0, 'return': -0.06},
        ]

    elif choice == '4':
        # News Sentiment
        print("\n📰 News-Sentiment Strategie:")
        print("   - Sentiment > 0.6 → BUY")
        print("   - Sentiment < -0.6 → SELL")

        samples = [
            # Sehr positive News
            {'rsi': 50, 'news_sentiment': 0.8, 'label': 2, 'return': 0.05},
            {'rsi': 55, 'news_sentiment': 0.7, 'label': 2, 'return': 0.04},

            # Sehr negative News
            {'rsi': 50, 'news_sentiment': -0.8, 'label': 0, 'return': -0.05},
            {'rsi': 45, 'news_sentiment': -0.7, 'label': 0, 'return': -0.04},
        ]

    else:
        print("❌ Ungültige Auswahl!")
        return

    # Samples speichern
    symbol = input("\nSymbol [BTC/USD]: ").strip() or "BTC/USD"

    for sample in samples:
        # Vollständige Features erstellen
        features = {
            'rsi': sample.get('rsi', 50),
            'macd': sample.get('macd', 0),
            'price_vs_sma50': sample.get('price_vs_sma50', 0),
            'volume_ratio': sample.get('volume_ratio', 1.0),
            'news_sentiment': sample.get('news_sentiment', 0)
        }

        db.save_training_data({
            'symbol': symbol,
            'timestamp': datetime.now(UTC).isoformat(),
            'features': json.dumps(features),
            'label': sample['label'],
            'future_return': sample['return'],
            'news_sentiment': features['news_sentiment']
        })

    print(f"\n✅ {len(samples)} Training-Samples gespeichert!")


def show_training_data(db):
    """Zeigt aktuelle Training-Daten."""
    print("\n--- AKTUELLE TRAINING-DATEN ---\n")

    samples = db.get_training_data(limit=20)

    if not samples:
        print("⚠️  Noch keine Training-Daten vorhanden.")
        return

    print(f"Total Samples: {len(samples)}\n")

    # Label-Verteilung
    labels = [s['label'] for s in samples]
    sell_count = labels.count(0)
    hold_count = labels.count(1)
    buy_count = labels.count(2)

    print(f"Label-Verteilung:")
    print(f"  SELL: {sell_count}")
    print(f"  HOLD: {hold_count}")
    print(f"  BUY:  {buy_count}")

    print(f"\nLetzte 5 Samples:")
    for i, sample in enumerate(samples[:5], 1):
        label_str = 'SELL' if sample['label'] == 0 else 'HOLD' if sample['label'] == 1 else 'BUY'
        features = json.loads(sample['features']) if isinstance(sample['features'], str) else sample['features']
        print(f"{i}. {sample['symbol']} → {label_str}")
        print(f"   Features: RSI={features.get('rsi', 'N/A')}, MACD={features.get('macd', 'N/A')}")
        print(f"   Return: {sample.get('future_return', 0)*100:+.2f}%")
        print()


def import_from_file(db):
    """Importiert Training-Daten aus Text-Datei."""
    print("\n--- IMPORT AUS TEXT-DATEI ---\n")

    filepath = input("Dateipfad (z.B. knowledge/rules.txt): ").strip()

    if not Path(filepath).exists():
        print(f"❌ Datei nicht gefunden: {filepath}")
        return

    print(f"\n📖 Lese {filepath}...")
    # TODO: Implementiere Parser für Text-Regeln
    print("⚠️  Diese Funktion ist noch nicht implementiert.")
    print("Siehe docs/KI_WISSEN_BEIBRINGEN.md für Details zur Knowledge Base.")


def main():
    """Hauptfunktion."""
    db = get_database()

    while True:
        show_menu()
        choice = input("Auswahl (1-5): ").strip()

        if choice == '1':
            add_single_sample(db)
        elif choice == '2':
            add_strategy_batch(db)
        elif choice == '3':
            show_training_data(db)
        elif choice == '4':
            import_from_file(db)
        elif choice == '5':
            print("\n👋 Tschüss!\n")
            break
        else:
            print("\n❌ Ungültige Auswahl!")

        input("\nDrücke Enter um fortzufahren...")

    db.close()


if __name__ == "__main__":
    main()
