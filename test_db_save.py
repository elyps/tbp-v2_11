#!/usr/bin/env python
"""Test ob DB-Speicherung funktioniert"""

import sys
from pathlib import Path
from datetime import datetime, UTC
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.database import get_database

# Get database instance
db = get_database()

print("=== Testing database save operations ===\n")

# Test 1: Save a test trade
test_trade = {
    'id': str(uuid.uuid4()),
    'symbol': 'TEST/EUR',
    'action': 'buy',
    'amount': 0.1,
    'price': 1000.0,
    'timestamp': datetime.now(UTC).isoformat(),
    'status': 'open',
    'strategy': 'test',
    'confidence': 0.75,
    'reason': 'Testing DB save',
    'stop_loss': 950.0,
    'take_profit': 1100.0
}

try:
    print("1. Saving test trade...")
    trade_id = db.save_trade(test_trade)
    print(f"   ✓ Trade saved with ID: {trade_id}")
except Exception as e:
    print(f"   ✗ Error saving trade: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Read it back
try:
    print("\n2. Reading trade back...")
    trades = db.get_trades(symbol='TEST/EUR')
    if trades:
        print(f"   ✓ Found {len(trades)} trade(s)")
        for t in trades:
            print(f"      {t['symbol']} {t['action']} {t['amount']} @ {t['price']}")
    else:
        print("   ✗ No trades found!")
except Exception as e:
    print(f"   ✗ Error reading trades: {e}")

# Test 3: Save a test position
test_position = {
    'symbol': 'TEST/EUR',
    'amount': 0.1,
    'entry_price': 1000.0,
    'current_price': 1050.0,
    'pnl': 5.0,
    'pnl_percent': 5.0,
    'opened_at': datetime.now(UTC).isoformat()
}

try:
    print("\n3. Saving test position...")
    db.save_position(test_position)
    print("   ✓ Position saved")
except Exception as e:
    print(f"   ✗ Error saving position: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Read positions
try:
    print("\n4. Reading positions back...")
    positions = db.get_open_positions()
    if positions:
        print(f"   ✓ Found {len(positions)} position(s)")
        for p in positions:
            print(f"      {p['symbol']}: {p['amount']} @ {p['entry_price']}")
    else:
        print("   ✗ No positions found!")
except Exception as e:
    print(f"   ✗ Error reading positions: {e}")

print("\n=== Test complete ===")
