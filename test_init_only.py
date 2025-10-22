#!/usr/bin/env python
"""
Testet nur die Bot-Initialisierung ohne den Loop zu starten.
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.bot import TradingBot
from trading_bot.database import get_database

def main():
    """Testet Bot-Initialisierung."""

    db = get_database('trading_bot.db')

    print("VOR BOT-INIT:")
    portfolio = db.get_portfolio()
    print(f"  Balance: €{portfolio['balance']:.2f}")
    print(f"  Equity:  €{portfolio['equity']:.2f}")
    print()

    print("Bot wird initialisiert (mit initial_balance=100)...")

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

    bot = TradingBot(config=paper_trading_config)
    print()

    print("NACH BOT-INIT:")
    print(f"  Bot-Memory: Balance=€{bot.portfolio['balance']:.2f}, Equity=€{bot.portfolio['equity']:.2f}")

    portfolio = db.get_portfolio()
    print(f"  DB:         Balance=€{portfolio['balance']:.2f}, Equity=€{portfolio['equity']:.2f}")
    print()

    if portfolio['balance'] == 100.0 and portfolio['equity'] == 100.0:
        print("✓ Portfolio korrekt!")
    else:
        print(f"❌ Portfolio falsch! Sollte 100€ sein, ist aber Balance={portfolio['balance']}, Equity={portfolio['equity']}")

    db.close()

if __name__ == "__main__":
    main()
