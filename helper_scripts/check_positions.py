#!/usr/bin/env python
"""
Prüft offene Positionen in der Datenbank.
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.database import get_database

def main():
    """Prüft offene Positionen."""
    db = get_database('trading_bot.db')

    print("=== PORTFOLIO ===")
    portfolio = db.get_portfolio()
    if portfolio:
        print(f"Balance: €{portfolio['balance']}")
        print(f"Equity:  €{portfolio['equity']}")
    else:
        print("Kein Portfolio gefunden")
    print()

    print("=== OFFENE POSITIONEN ===")
    positions = db.get_all_positions()
    if positions:
        for pos in positions:
            print(f"{pos['symbol']}: {pos['amount']} @ €{pos['entry_price']} (P&L: €{pos.get('pnl', 0.0)})")
    else:
        print("Keine offenen Positionen")
    print()

    print("=== OFFENE TRADES ===")
    trades = db.get_open_trades()
    if trades:
        for trade in trades:
            print(f"{trade['symbol']}: {trade['action']} {trade['amount']} @ €{trade['price']}")
    else:
        print("Keine offenen Trades")
    print()

    db.close()

if __name__ == "__main__":
    main()
