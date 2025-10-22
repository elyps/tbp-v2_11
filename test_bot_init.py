#!/usr/bin/env python
"""
Testet die Bot-Initialisierung und zeigt Portfolio-Werte.
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.bot import TradingBot
from trading_bot.database import get_database

def main():
    """Testet die Bot-Initialisierung."""

    # Datenbank zurücksetzen
    print("1. Setze Datenbank zurück...")
    db = get_database('trading_bot.db')
    db.save_portfolio({
        'balance': 100.0,
        'equity': 100.0,
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_pnl': 0.0,
        'max_drawdown': 0.0,
        'sharpe_ratio': 0.0
    })
    portfolio = db.get_portfolio()
    print(f"   Nach Reset: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print()

    # Bot initialisieren (wie in run_paper_trading.py)
    print("2. Initialisiere Bot mit 100€ Config...")
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

    # Prüfe Portfolio im Bot
    print("3. Portfolio im Bot nach Initialisierung:")
    print(f"   Bot-Portfolio: Balance=€{bot.portfolio['balance']}, Equity=€{bot.portfolio['equity']}")
    print()

    # Prüfe Portfolio in DB
    print("4. Portfolio in Datenbank nach Bot-Init:")
    portfolio = db.get_portfolio()
    print(f"   DB-Portfolio: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print()

    if portfolio['balance'] == 100.0 and portfolio['equity'] == 100.0:
        print("✓ Portfolio ist korrekt auf 100€!")
    else:
        print(f"❌ Portfolio ist falsch! Erwartet 100€, aber Balance={portfolio['balance']}, Equity={portfolio['equity']}")

    db.close()

if __name__ == "__main__":
    main()
