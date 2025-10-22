# Problem Analysis: Trades not showing in Dashboard

## Symptom
- Bot generates signals with 74.8% confidence
- Bot shows balance of €69.97 (down from €100)
- Bot has open position in ETH/EUR (0.0092 ETH)
- **BUT:** Dashboard shows €100, 0 trades, 0 positions

## Root Cause
Trades are being executed **in memory only** (in `self.portfolio` dict), but **NOT being persisted to the database**.

## Evidence

### 1. Bot Memory State (from logs)
```
balance=69.97
open_positions={'ETH/EUR': 0.009184563809757068}
```

### 2. Database State
```
Portfolio: balance=100.0, equity=100.0
Trades: 0
Positions: 0
```

### 3. Code Flow
The bot DOES attempt to save trades:
- `bot.py:556` - `self.db.save_trade(trade)` in try/except
- `bot.py:598` - `self.db.save_position({...})` in try/except

Errors are caught and logged but NOT thrown, so bot continues running.

## Why No Error Logs?
Looking at recent logs (12:35), we see:
```
WARNING - Modell ist noch nicht trainiert. Gebe Standardwerte zurück.
```

The ML model wasn't loading because `feature_names.json` was missing (only `.txt` existed).
**Fixed:** Created `feature_names.json`

## Why New Signals Are Rejected
RiskManager rejects new BUY signals for ETH/EUR because:
```python
if symbol in open_positions:
    logger.info("RiskManager: BUY verworfen, %s bereits offen", symbol)
    continue
```

The position exists in memory, so no new trades are created.

## Questions to Investigate
1. **When were the original trades created?** (The ones that exist in memory but not in DB)
2. **Why didn't those trades get saved to the database?**
3. **Is the bot currently running?** If yes, with which script?

## Possible Causes
1. Database connection issue during initial trades
2. Different database file being used (check if multiple `.db` files exist)
3. Bot was started without proper database initialization
4. Transactions not being committed

## Next Steps
1. Check if bot is currently running
2. If yes, stop it and restart it properly after fixes
3. Reset portfolio to clear memory state
4. Ensure model loads correctly (feature_names.json now exists)
5. Monitor if new trades are saved to DB
