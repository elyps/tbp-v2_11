#!/usr/bin/env python
"""
Setzt das Portfolio auf 100€ zurück und löscht alle Positionen und Trades.
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.database import get_database

def main():
    """Setzt das Portfolio auf 100€ zurück."""
    db = get_database('trading_bot.db')

    # Hole aktuelles Portfolio
    portfolio = db.get_portfolio()
    positions = db.get_all_positions()
    open_trades = db.get_open_trades()

    if portfolio:
        print(f"Aktuelles Portfolio:")
        print(f"  Balance: €{portfolio['balance']:.2f}")
        print(f"  Equity:  €{portfolio['equity']:.2f}")
        print(f"  Offene Positionen: {len(positions)}")
        print(f"  Offene Trades: {len(open_trades)}")
        print()
    else:
        print("Kein Portfolio in der Datenbank gefunden.")
        print()

    # Lösche alle offenen Positionen
    if positions:
        print(f"Lösche {len(positions)} offene Positionen...")
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM positions")
        db.conn.commit()

    # Lösche alle offenen Trades (optional: alle Trades löschen)
    if open_trades:
        print(f"Lösche {len(open_trades)} offene Trades...")
        cursor = db.conn.cursor()
        cursor.execute("DELETE FROM trades WHERE status = 'open'")
        db.conn.commit()

    # Setze Portfolio auf 100€ zurück
    print("Setze Portfolio auf 100€ zurück...")

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

    # Bestätige
    portfolio = db.get_portfolio()
    positions = db.get_all_positions()
    print()
    print(f"Neues Portfolio:")
    print(f"  Balance: €{portfolio['balance']:.2f}")
    print(f"  Equity:  €{portfolio['equity']:.2f}")
    print(f"  Offene Positionen: {len(positions)}")
    print()
    print("✓ Portfolio erfolgreich zurückgesetzt!")

    db.close()

if __name__ == "__main__":
    main()
