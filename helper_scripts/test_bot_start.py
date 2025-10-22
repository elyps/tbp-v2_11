#!/usr/bin/env python
"""
Startet den Bot kurz und prüft das Portfolio danach.
"""

import sys
import threading
import time
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.bot import TradingBot
from trading_bot.database import get_database

def main():
    """Startet den Bot und prüft Portfolio."""

    print("=" * 60)
    print("VOR BOT-START")
    print("=" * 60)

    db = get_database('trading_bot.db')
    portfolio = db.get_portfolio()
    print(f"DB-Portfolio: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print()

    print("=" * 60)
    print("STARTE BOT (wie in run_paper_trading.py)")
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

    # Bot initialisieren
    bot = TradingBot(config=paper_trading_config)
    print()

    print("=" * 60)
    print("BOT WURDE INITIALISIERT")
    print("=" * 60)
    print(f"Bot-Portfolio: Balance=€{bot.portfolio['balance']}, Equity=€{bot.portfolio['equity']}")
    print()

    print("=" * 60)
    print("PRÜFE DATENBANK NACH BOT-INIT")
    print("=" * 60)
    portfolio = db.get_portfolio()
    positions = db.get_all_positions()
    print(f"DB-Portfolio: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print(f"Offene Positionen: {len(positions)}")

    if positions:
        print("\nPositionen:")
        for pos in positions:
            print(f"  - {pos['symbol']}: {pos['amount']} @ €{pos['entry_price']}")
    print()

    # Starte Bot für 10 Sekunden
    print("=" * 60)
    print("STARTE BOT-LOOP FÜR 10 SEKUNDEN...")
    print("=" * 60)

    def run_bot():
        try:
            bot.run(symbols=['BTC/EUR'])
        except Exception as e:
            print(f"Bot-Fehler: {e}")

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    time.sleep(10)
    bot.stop()

    print()
    print("=" * 60)
    print("BOT GESTOPPT - FINALE PRÜFUNG")
    print("=" * 60)

    portfolio = db.get_portfolio()
    positions = db.get_all_positions()
    print(f"DB-Portfolio: Balance=€{portfolio['balance']}, Equity=€{portfolio['equity']}")
    print(f"Offene Positionen: {len(positions)}")

    if positions:
        print("\nPositionen:")
        for pos in positions:
            print(f"  - {pos['symbol']}: {pos['amount']} @ €{pos['entry_price']}")

    print()
    if portfolio['equity'] != 100.0:
        print(f"❌ PROBLEM! Equity wurde von 100€ auf {portfolio['equity']}€ geändert!")
    else:
        print("✓ Equity ist korrekt bei 100€")

    db.close()

if __name__ == "__main__":
    main()
