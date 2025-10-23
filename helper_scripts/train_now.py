"""
TRAIN NOW - Trainiert die KI sofort mit aktuellen Daten
Wartet NICHT auf 24h oder 100 Samples - trainiert JETZT!
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_bot.database import get_database
from trading_bot.ml_model import MLModel
from config_paths import MODELS_DIR
import pandas as pd
import numpy as np
import json
from datetime import datetime

# UTC import
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


def train_model_now(min_samples: int = 5):
    """
    Trainiert das Modell SOFORT mit den aktuellen Daten in der DB.

    Args:
        min_samples: Minimale Anzahl Samples (Standard: 5 statt 100)
    """
    print("\n" + "=" * 70)
    print("🧠 KI SOFORT TRAINIEREN")
    print("=" * 70)

    db = get_database()

    # 1. Hole Training-Daten aus DB
    print("\n[1/5] Lade Training-Daten aus Datenbank...")
    training_samples = db.get_training_data(limit=100000)

    if len(training_samples) < min_samples:
        print(f"\n❌ Nicht genug Samples!")
        print(f"   Vorhanden: {len(training_samples)}")
        print(f"   Benötigt:  {min_samples}")
        print(f"\n💡 Füge mehr Daten hinzu mit:")
        print(f"   python helper_scripts/teach_ai.py")
        print(f"   python helper_scripts/quick_teach_example.py")
        db.close()
        return False

    print(f"✓ {len(training_samples)} Training-Samples geladen")

    # 2. Bereite Daten vor
    print("\n[2/5] Bereite Daten vor...")

    # training_samples ist bereits ein DataFrame!
    df_samples = training_samples

    # Extrahiere Labels
    if 'label' not in df_samples.columns:
        print("❌ Keine Labels in den Daten gefunden!")
        db.close()
        return False

    y = df_samples['label'].values

    # Feature-Spalten identifizieren (alles außer label, symbol, timestamp, pnl)
    exclude_cols = ['label', 'symbol', 'timestamp', 'pnl', 'id', 'trade_id', 'future_return']
    feature_cols = [col for col in df_samples.columns if col not in exclude_cols]

    if not feature_cols:
        print("❌ Keine Features gefunden!")
        db.close()
        return False

    print(f"✓ Features erkannt: {', '.join(feature_cols)}")

    # Extrahiere Features
    X = df_samples[feature_cols].values

    # Label-Verteilung anzeigen
    unique, counts = np.unique(y, return_counts=True)
    label_dist = dict(zip(unique, counts))
    print(f"\n📊 Label-Verteilung:")
    print(f"   SELL (0): {label_dist.get(0, 0)}")
    print(f"   HOLD (1): {label_dist.get(1, 0)}")
    print(f"   BUY  (2): {label_dist.get(2, 0)}")

    # 3. Erstelle DataFrame für MLModel
    print(f"\n[3/5] Erstelle Training-Set...")
    X_df = pd.DataFrame(X, columns=feature_cols)
    y_series = pd.Series(y)

    print(f"✓ Training-Set: {len(X_df)} Samples × {len(feature_cols)} Features")

    # 4. Trainiere Modell
    print(f"\n[4/5] Trainiere KI-Modell...")
    print("⏳ Dies kann einige Sekunden dauern...")

    ml_model = MLModel(settings={
        'model_type': 'xgboost',
        'enable_predictions': True
    })

    try:
        # Training durchführen
        ml_model.train(X_df, y_series)
        print("✓ Training abgeschlossen!")

    except Exception as e:
        print(f"❌ Fehler beim Training: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False

    # 5. Evaluiere Modell
    print(f"\n[5/5] Evaluiere Performance...")

    accuracy = 0.0  # Default value

    try:
        # Vorhersagen auf Training-Daten
        predictions = ml_model.predict(X_df)

        # Check if 'prediction' exists, otherwise try direct prediction
        if isinstance(predictions, dict) and 'prediction' in predictions:
            pred_labels = predictions['prediction'].values
        elif isinstance(predictions, pd.DataFrame) and 'prediction' in predictions.columns:
            pred_labels = predictions['prediction'].values
        else:
            # Fallback: Use the predictions directly
            pred_labels = predictions if isinstance(predictions, np.ndarray) else predictions.values

        # Accuracy berechnen
        accuracy = (pred_labels == y_series).mean()

        # Confusion Matrix
        from collections import Counter
        correct_by_label = {}
        total_by_label = Counter(y_series)

        for true_label, pred_label in zip(y_series, pred_labels):
            if true_label == pred_label:
                correct_by_label[true_label] = correct_by_label.get(true_label, 0) + 1

        print(f"\n📊 PERFORMANCE:")
        print(f"   Gesamt-Accuracy: {accuracy*100:.1f}%")
        print(f"\n   Pro Klasse:")
        for label in [0, 1, 2]:
            label_name = ['SELL', 'HOLD', 'BUY'][label]
            correct = correct_by_label.get(label, 0)
            total = total_by_label.get(label, 0)
            acc = (correct / total * 100) if total > 0 else 0
            print(f"   {label_name}: {acc:.1f}% ({correct}/{total})")

        # Speichere Performance in DB
        db.save_model_performance({
            'timestamp': datetime.now(UTC).isoformat(),
            'accuracy': float(accuracy),
            'samples_count': len(X_df),
            'features_count': len(feature_cols),
            'model_version': 'manual_train'
        })

        print(f"\n✓ Performance gespeichert")

    except Exception as e:
        print(f"⚠️  Konnte Performance nicht evaluieren: {e}")

    db.close()

    # 6. Zusammenfassung
    print("\n" + "=" * 70)
    print("✅ TRAINING ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 70)
    print(f"\n📊 Trainiert mit:")
    print(f"   • {len(X_df)} Samples")
    print(f"   • {len(feature_cols)} Features")
    print(f"   • Accuracy: {accuracy*100:.1f}%")
    print(f"\n💾 Modell gespeichert in: {MODELS_DIR}")
    print(f"\n🚀 Nächste Schritte:")
    print(f"   1. Bot starten: python run_paper_trading.py")
    print(f"   2. Dashboard: python ai_learning_dashboard.py")
    print(f"   3. Mehr Daten: python helper_scripts/teach_ai.py")
    print()

    return True


def show_current_stats():
    """Zeigt aktuelle Training-Daten Statistiken."""
    db = get_database()

    samples = db.get_training_data(limit=100000)
    print(f"\n📊 Aktuelle Daten:")
    print(f"   Training-Samples: {len(samples)}")

    if not samples.empty:
        labels = samples['label'].values
        print(f"   SELL: {(labels == 0).sum()}")
        print(f"   HOLD: {(labels == 1).sum()}")
        print(f"   BUY:  {(labels == 2).sum()}")

    # Model Performance Historie
    perf = db.get_model_performance_history(limit=5)
    if perf:
        print(f"\n🧠 Letzte Trainings:")
        for p in perf[:3]:
            timestamp = p.get('timestamp', '')[:16]
            accuracy = p.get('accuracy', 0) * 100
            samples = p.get('samples_count', 0)
            print(f"   {timestamp}: {accuracy:.1f}% ({samples} samples)")

    db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Trainiert die KI sofort')
    parser.add_argument('--min-samples', type=int, default=5,
                        help='Minimale Anzahl Samples (default: 5)')
    parser.add_argument('--stats', action='store_true',
                        help='Zeige nur Statistiken, trainiere nicht')

    args = parser.parse_args()

    if args.stats:
        show_current_stats()
    else:
        success = train_model_now(min_samples=args.min_samples)
        sys.exit(0 if success else 1)
