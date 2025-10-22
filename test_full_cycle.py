#!/usr/bin/env python
"""
Testet den vollständigen Zyklus: Reset + Bot-Init + Dashboard-Check
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.bot import TradingBot
from trading_bot.database import get_database

def main():
    """Testet den vollständigen Zyklus."""

    print("=" * 60)
    print("SCHRITT 1: Reset Portfolio auf 100€")
    print("=" * 60)

    db = get_database('trading_bot.db')

    # Lösche Positionen
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM positions")
    db.conn.commit()

    # Setze Portfolio zurück
    new_portfolio = {
        'balance': 100.0,
        'equity': 100.0,
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_pnl': 0.0,
        'max_drawdown': 0.0,
        'sharpe_ratio': 0.0
    }
    db.save_portfolio(new_portfolio)

    portfolio = db.get_portfolio()
    print(f"✓ Portfolio: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print()

    print("=" * 60)
    print("SCHRITT 2: Bot initialisieren (wie in run_paper_trading.py)")
    print("=" * 60)

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
    print(f"✓ Bot initialisiert")
    print(f"  Bot-Portfolio: Balance=€{bot.portfolio['balance']}, Equity=€{bot.portfolio['equity']}")
    print()

    print("=" * 60)
    print("SCHRITT 3: Prüfe Datenbank nach Bot-Init")
    print("=" * 60)

    portfolio = db.get_portfolio()
    positions = db.get_all_positions()
    print(f"DB-Portfolio: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print(f"Offene Positionen: {len(positions)}")
    print()

    print("=" * 60)
    print("ERGEBNIS")
    print("=" * 60)

    if portfolio['balance'] == 100.0 and portfolio['equity'] == 100.0:
        print("✓✓✓ ERFOLG! Portfolio ist korrekt auf 100€!")
    else:
        print(f"❌ FEHLER! Portfolio ist falsch:")
        print(f"   Erwartet: Balance=100.0, Equity=100.0")
        print(f"   Erhalten: Balance={portfolio['balance']}, Equity={portfolio['equity']}")

    db.close()

if __name__ == "__main__":
    main()
