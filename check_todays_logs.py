from pathlib import Path
from datetime import datetime

log_file = Path(__file__).parent / 'logs' / 'trading_bot.log'

today = datetime.now().strftime('2025-10-22')  # Today's date

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Filter today's logs
todays_logs = [line for line in lines if today in line]

print(f"=== LOGS FROM {today} ===")
print(f"Total lines today: {len(todays_logs)}")

print("\n=== ERRORS TODAY ===")
errors_found = False
for line in todays_logs:
    if 'ERROR' in line or 'Fehler beim Speichern' in line:
        print(line.strip())
        errors_found = True

if not errors_found:
    print("No errors found")

print("\n=== SIGNALS GENERATED TODAY ===")
signals = []
for line in todays_logs:
    if 'Handelssignal(e)' in line and 'generiert' in line:
        signals.append(line.strip())

print(f"Found {len(signals)} signal generation events")
for sig in signals[-10:]:  # Last 10
    print(sig)

print("\n=== TRADE DECISIONS TODAY ===")
decisions = []
for line in todays_logs:
    if 'Handelsentscheidung(en) nach Risikomanagement' in line:
        decisions.append(line.strip())

print(f"Found {len(decisions)} trade decision events")
for dec in decisions[-10:]:  # Last 10
    print(dec)

print("\n=== TRADES EXECUTED TODAY ===")
executed = []
for line in todays_logs:
    if 'Kauforder ausgeführt' in line or 'Verkaufsorder ausgeführt' in line:
        executed.append(line.strip())

print(f"Found {len(executed)} executed orders")
for ex in executed[-10:]:  # Last 10
    print(ex)

print("\n=== TRADES RECORDED TODAY ===")
recorded = []
for line in todays_logs:
    if 'Trade aufgezeichnet' in line:
        recorded.append(line.strip())

print(f"Found {len(recorded)} recorded trades")
for rec in recorded[-10:]:  # Last 10
    print(rec)

print("\n=== REJECTED BY RISK MANAGEMENT ===")
for line in todays_logs:
    if 'Alle Signale vom Risikomanagement abgelehnt' in line:
        print(line.strip())
