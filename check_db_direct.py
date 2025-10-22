import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'trading_bot.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== TRADES ===")
cursor.execute("SELECT COUNT(*) FROM trades")
print(f"Total trades: {cursor.fetchone()[0]}")

cursor.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 5")
trades = cursor.fetchall()
if trades:
    for trade in trades:
        print(trade)
else:
    print("No trades found")

print("\n=== PORTFOLIO ===")
cursor.execute("SELECT * FROM portfolio ORDER BY id DESC LIMIT 1")
portfolio = cursor.fetchone()
if portfolio:
    print(portfolio)
else:
    print("No portfolio data")

print("\n=== POSITIONS ===")
cursor.execute("SELECT COUNT(*) FROM positions")
print(f"Total positions: {cursor.fetchone()[0]}")

cursor.execute("SELECT * FROM positions")
positions = cursor.fetchall()
if positions:
    for pos in positions:
        print(pos)
else:
    print("No positions found")

conn.close()
