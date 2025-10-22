#!/usr/bin/env python
"""
Testet das Dashboard einmalig ohne Loop.
"""

import sys
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.database import get_database
from paper_trading_dashboard import print_dashboard

def main():
    """Testet das Dashboard."""
    start_capital = 100.0
    db_path = 'trading_bot.db'

    if not Path(db_path).exists():
        print(f"Datenbank '{db_path}' nicht gefunden.")
        sys.exit(1)

    db = get_database(db_path)
    print_dashboard(db, start_capital)
    db.close()

if __name__ == "__main__":
    main()
