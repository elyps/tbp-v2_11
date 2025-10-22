#!/usr/bin/env python
"""
Debug-Skript um die Config-Werte zu überprüfen.
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.config import DEFAULT_SETTINGS

def main():
    """Zeigt die Config-Werte an."""

    print("DEFAULT_SETTINGS aus config.py:")
    print(f"  initial_balance: {DEFAULT_SETTINGS.get('initial_balance')}")
    print()

    # Simuliere die Config wie in run_paper_trading.py
    paper_trading_config = {
        'settings': {
            'initial_balance': 100.0,
            'paper_trading': True,
            'use_enhanced_pipeline': False,
        },
        'strategies': {
            'ml_based': {'enabled': True, 'min_confidence': 0.70},
            'trend_following': {'enabled': False},
            'mean_reversion': {'enabled': False},
        }
    }

    print("paper_trading_config aus run_paper_trading.py:")
    print(f"  initial_balance: {paper_trading_config['settings'].get('initial_balance')}")
    print()

    # Simuliere den Merge wie in bot.py _load_config()
    merged_settings = {**DEFAULT_SETTINGS, **paper_trading_config.get('settings', {})}

    print("Nach Merge (wie in bot._load_config()):")
    print(f"  initial_balance: {merged_settings.get('initial_balance')}")
    print()

    if merged_settings.get('initial_balance') == 100.0:
        print("✓ Config-Merge funktioniert korrekt!")
    else:
        print("❌ Config-Merge überschreibt initial_balance NICHT korrekt!")
        print(f"   Erwartet: 100.0, Erhalten: {merged_settings.get('initial_balance')}")

if __name__ == "__main__":
    main()
