from pathlib import Path

log_file = Path(__file__).parent / 'logs' / 'trading_bot.log'

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Get last 300 lines
recent_lines = lines[-300:]

print("=== ERRORS IN RECENT LOGS ===")
errors_found = False
for line in recent_lines:
    if 'ERROR' in line or 'Fehler beim Speichern' in line:
        print(line.strip())
        errors_found = True

if not errors_found:
    print("No errors found in recent logs")

print("\n=== TRADE EXECUTION IN RECENT LOGS ===")
for line in recent_lines:
    if 'Kauforder ausgeführt' in line or 'Verkaufsorder ausgeführt' in line:
        print(line.strip())

print("\n=== TRADE RECORDING IN RECENT LOGS ===")
for line in recent_lines:
    if 'Trade aufgezeichnet' in line:
        print(line.strip())
