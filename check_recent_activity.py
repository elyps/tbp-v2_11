from pathlib import Path

log_file = Path(__file__).parent / 'logs' / 'trading_bot.log'

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Get last 100 lines
recent = lines[-100:]

print("=== LAST 100 LINES ===")
for line in recent:
    if '2025-10-22' in line:
        # Only show INFO and higher, skip DEBUG
        if any(level in line for level in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']):
            print(line.strip())
