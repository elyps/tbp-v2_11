"""
Test Portfolio Persistence - Prüft ob Portfolio korrekt aus DB geladen wird
"""
import sys
from pathlib import Path
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_bot.database import get_database
from config_paths import DB_PATH
from trading_bot.bot import TradingBot

# UTC import
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


def test_portfolio_persistence():
    """Testet ob Portfolio korrekt aus DB geladen wird."""

    print("=" * 70)
    print("TEST: Portfolio Persistence")
    print("=" * 70)

    # Hole DB
    db = get_database(str(DB_PATH))

    # === PHASE 1: Erstelle Trade und Position in DB ===
    print("\n[PHASE 1] Erstelle Test-Daten in DB...")

    # Erstelle einen Test-Trade (BUY)
    test_trade = {
        'id': str(uuid.uuid4()),
        'symbol': 'ETH/USD',
        'action': 'buy',
        'amount': 0.05,
        'price': 2500.0,
        'timestamp': datetime.now(UTC).isoformat(),
        'status': 'open',
        'strategy': 'test',
        'confidence': 0.9,
        'reason': 'Test Purchase',
        'stop_loss': 2400.0,
        'take_profit': 2700.0
    }

    db.save_trade(test_trade)
    print(f"✓ Trade gespeichert: {test_trade['symbol']} {test_trade['action']}")

    # Erstelle Test-Position
    test_position = {
        'symbol': 'ETH/USD',
        'amount': 0.05,
        'entry_price': 2500.0,
        'current_price': 2500.0,
        'pnl': 0.0,
        'pnl_percent': 0.0,
        'opened_at': datetime.now(UTC).isoformat()
    }

    db.save_position(test_position)
    print(f"✓ Position gespeichert: {test_position['symbol']} {test_position['amount']}")

    # Speichere Portfolio-Status
    cost = test_trade['amount'] * test_trade['price'] + (test_trade['amount'] * test_trade['price'] * 0.001)  # mit 0.1% Fee
    new_balance = 100.0 - cost

    portfolio_data = {
        'balance': new_balance,
        'equity': 100.0,  # Balance + unrealized PnL
        'total_trades': 1,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_pnl': 0.0,
        'max_drawdown': 0.0,
        'sharpe_ratio': 0.0
    }

    db.save_portfolio(portfolio_data)
    print(f"✓ Portfolio gespeichert: Balance=€{new_balance:.2f}, Equity=€100.00")

    # === PHASE 2: Erstelle neuen Bot (sollte Portfolio laden) ===
    print("\n[PHASE 2] Erstelle Bot (sollte Portfolio aus DB laden)...")

    bot = TradingBot()

    # Prüfe Portfolio
    print(f"\nBot Portfolio:")
    print(f"  Balance: €{bot.portfolio['balance']:.2f}")
    print(f"  Equity: €{bot.portfolio['equity']:.2f}")
    print(f"  Positionen: {len(bot.portfolio['positions'])}")
    print(f"  Trades: {len(bot.portfolio['trades'])}")

    # Validierung
    success = True

    if len(bot.portfolio['positions']) == 0:
        print("\n❌ FEHLER: Keine Positionen geladen!")
        success = False
    else:
        print(f"✓ Positionen geladen: {list(bot.portfolio['positions'].keys())}")

        # Prüfe ETH Position
        if 'ETH/USD' in bot.portfolio['positions']:
            eth_pos = bot.portfolio['positions']['ETH/USD']
            price_key = 'avg_price' if 'avg_price' in eth_pos else 'entry_price'
            print(f"  ETH/USD: {eth_pos['amount']} @ €{eth_pos[price_key]:.2f}")
        else:
            print("❌ FEHLER: ETH/USD Position nicht gefunden!")
            success = False

    if len(bot.portfolio['trades']) == 0:
        print("❌ FEHLER: Keine Trades geladen!")
        success = False
    else:
        print(f"✓ Trades geladen: {len(bot.portfolio['trades'])}")

    if abs(bot.portfolio['balance'] - new_balance) > 0.01:
        print(f"❌ FEHLER: Balance falsch! Erwartet: €{new_balance:.2f}, Erhalten: €{bot.portfolio['balance']:.2f}")
        success = False
    else:
        print(f"✓ Balance korrekt: €{bot.portfolio['balance']:.2f}")

    db.close()

    print("\n" + "=" * 70)
    if success:
        print("✅ TEST ERFOLGREICH - Portfolio wird korrekt aus DB geladen!")
    else:
        print("❌ TEST FEHLGESCHLAGEN - Portfolio-Laden funktioniert nicht!")
    print("=" * 70)

    return success


if __name__ == "__main__":
    success = test_portfolio_persistence()
    sys.exit(0 if success else 1)
