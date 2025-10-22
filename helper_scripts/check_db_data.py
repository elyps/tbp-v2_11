"""
Quick database check - what's actually in there?
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_bot.database import get_database
from config_paths import DB_PATH

db = get_database(str(DB_PATH))

print(f"Database: {DB_PATH}")
print("=" * 70)

# Trades
trades = db.get_trades(limit=10)
print(f"\n📊 TRADES: {len(trades)} found")
for t in trades[:3]:
    print(f"  - {t.get('symbol')} {t.get('action')} @ {t.get('price'):.2f}")

# Training Data
training = db.get_training_data(limit=10)
print(f"\n📚 TRAINING DATA: {len(training)} found")

# News
news = db.get_recent_news('BTC', limit=10, hours=24)
print(f"\n📰 NEWS: {len(news)} found")

# Model Performance
perf = db.get_model_performance_history(limit=10)
print(f"\n🧠 MODEL PERFORMANCE: {len(perf)} found")
if perf:
    for p in perf:
        print(f"  - Accuracy: {p.get('accuracy', 0)*100:.1f}% ({p.get('samples_count')} samples)")

db.close()
