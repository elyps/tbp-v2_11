"""
Test Database Save Operations
Prüft ob Trades und Training-Daten gespeichert werden können
"""
import sys
from pathlib import Path
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_bot.database import get_database
from config_paths import DB_PATH

# UTC import with fallback
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


def test_database():
    """Testet alle DB-Operationen."""
    print(f"Teste Datenbank: {DB_PATH}")
    print("=" * 70)

    db = get_database(str(DB_PATH))

    # Test 1: Trade speichern
    print("\n[TEST 1] Trade speichern...")
    test_trade = {
        'id': str(uuid.uuid4()),
        'symbol': 'BTC/USD',
        'action': 'buy',
        'amount': 0.001,
        'price': 67000.0,
        'timestamp': datetime.now(UTC).isoformat(),
        'status': 'open',
        'strategy': 'test',
        'confidence': 0.85,
        'reason': 'Database test',
        'stop_loss': 66000.0,
        'take_profit': 68000.0
    }

    try:
        trade_id = db.save_trade(test_trade)
        print(f"  ✓ Trade gespeichert (ID: {trade_id})")
    except Exception as e:
        print(f"  ✗ Fehler beim Speichern: {e}")
        return False

    # Test 2: Trade abrufen
    print("\n[TEST 2] Trade abrufen...")
    try:
        trades = db.get_trades(limit=5)
        print(f"  ✓ {len(trades)} Trades abgerufen")
        if trades:
            latest = trades[0]
            print(f"  ⊳ Letzter Trade: {latest['symbol']} {latest['action']} @ {latest['price']}")
    except Exception as e:
        print(f"  ✗ Fehler beim Abrufen: {e}")
        return False

    # Test 3: Training-Daten speichern
    print("\n[TEST 3] Training-Daten speichern...")
    test_training = {
        'symbol': 'BTC/USD',
        'timestamp': datetime.now(UTC).isoformat(),
        'features': '{"rsi": 45.5, "macd": 0.23, "sma_20": 67000}',
        'label': 2,  # BUY
        'future_return': 0.015,
        'news_sentiment': 0.3
    }

    try:
        db.save_training_data(test_training)
        print(f"  ✓ Training-Daten gespeichert")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

    # Test 4: Training-Daten abrufen
    print("\n[TEST 4] Training-Daten abrufen...")
    try:
        training_data = db.get_training_data(limit=5)
        print(f"  ✓ {len(training_data)} Training-Samples abgerufen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

    # Test 5: News speichern
    print("\n[TEST 5] News speichern...")
    test_news = {
        'symbol': 'BTC',
        'title': 'Test News Article',
        'description': 'This is a test',
        'url': 'https://example.com',
        'source': 'test',
        'published_at': datetime.now(UTC).isoformat(),
        'sentiment_score': 0.5,
        'sentiment_label': 'positive'
    }

    try:
        db.save_news(test_news)
        print(f"  ✓ News gespeichert")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

    # Test 6: News abrufen
    print("\n[TEST 6] News abrufen...")
    try:
        news = db.get_recent_news('BTC', limit=5, hours=24)
        print(f"  ✓ {len(news)} News-Artikel abgerufen")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

    # Test 7: Model Performance speichern
    print("\n[TEST 7] Model Performance speichern...")
    test_perf = {
        'timestamp': datetime.now(UTC).isoformat(),
        'accuracy': 0.72,
        'samples_used': 500,
        'features_count': 15
    }

    try:
        db.save_model_performance(test_perf)
        print(f"  ✓ Model Performance gespeichert")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

    # Test 8: Model Performance abrufen
    print("\n[TEST 8] Model Performance abrufen...")
    try:
        perf_history = db.get_model_performance_history(limit=5)
        print(f"  ✓ {len(perf_history)} Performance-Einträge abgerufen")
        if perf_history:
            latest_perf = perf_history[0]
            print(f"  ⊳ Letzte Accuracy: {latest_perf.get('accuracy', 0)*100:.1f}%")
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        return False

    db.close()

    print("\n" + "=" * 70)
    print("✓ ALLE TESTS ERFOLGREICH")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
