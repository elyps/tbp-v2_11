# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-powered cryptocurrency trading bot with Machine Learning integration for paper trading. The bot is currently configured for a 100€ paper trading challenge using ML-based strategies to generate buy/sell signals.

**Language**: Python 3.9+, with German comments and documentation throughout the codebase.

## Core Architecture

### Dual Pipeline System

The bot implements **two parallel trading pipelines**:

1. **Main Pipeline** (`trading_bot/`): Original bot implementation with integrated ML models, technical indicators, risk management, and continuous learning
2. **Enhanced Pipeline** (`trader/`): Companion Codex architecture with modular feature engineering, signal generation, position sizing, and risk management

The main bot (`trading_bot.bot.TradingBot`) conditionally imports and uses the enhanced pipeline if `use_enhanced_pipeline: True` in config. Both pipelines share the same SQLite database.

### Data Flow

```
Market Data (CCXT) → Data Provider → Technical Indicators → ML Model → Strategy Manager → Risk Manager → Exchange Interface → Database
```

The bot uses a centralized SQLite database (`data/trading_bot.db`) for all persistence:
- Portfolio state and equity tracking
- Trade history with P&L
- Open positions
- ML training samples
- Model performance metrics
- News and sentiment data
- Generated signals

### Key Components

**TradingBot** (`trading_bot/bot.py`): Main orchestrator that coordinates all components. Initializes portfolio from database, runs trading loop, and manages the decision cycle.

**Database** (`trading_bot/database.py`): Singleton SQLite manager accessed via `get_database()`. Creates tables on first run. All state is persisted here, NOT in JSON files.

**MLModel** (`trading_bot/ml_model.py`): Supports XGBoost (primary), LightGBM, RandomForest, and GradientBoosting. Model files stored in `models/trading_model.pkl` with scaler and feature names.

**StrategyManager** (`trading_bot/strategy.py`): Implements multiple strategies:
- `trend_following`: SMA/MACD/RSI based
- `mean_reversion`: Bollinger Bands + RSI
- `breakout`: ATR + volume analysis
- `ml_based`: Uses ML model predictions

**ContinuousLearner** (`trading_bot/continuous_learning.py`): Collects training data from live trades and retrains model periodically based on `min_samples_retrain` and `retrain_frequency_hours`.

**AILearningEngine** (`trading_bot/ai_learning_engine.py`): Advanced continuous learning system that:
- Collects news from CoinDesk, NewsAPI, CryptoCompare (every 4h)
- Collects market data from Kraken (every hour)
- Performs sentiment analysis on news
- Creates training samples with technical indicators + news sentiment
- Auto-retrains model every 24h
- Tracks model performance and accuracy improvements

See `docs/AI_CONTINUOUS_LEARNING.md` for detailed documentation.

## Common Commands

### Setup and Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (copy from docs/env.example.txt)
cp docs/env.example.txt .env
```

### Running the Bot
```bash
# Reset portfolio to €100 (ALWAYS do this before starting)
python helper_scripts/reset_portfolio.py

# Train the ML model (required before first run)
python train_comprehensive_model.py

# Start paper trading
python run_paper_trading.py

# Monitor with dashboard (run in separate terminal)
python paper_trading_dashboard.py
```

### Testing
```bash
# Run pytest tests
pytest trader/tests/

# Test bot initialization only
python helper_scripts/test_init_only.py

# Test full cycle (reset + init + start)
python helper_scripts/test_full_cycle.py

# Test dashboard data
python helper_scripts/test_dashboard.py
```

### Database Operations
```bash
# View database contents
python helper_scripts/view_database.py

# View trade history
python helper_scripts/view_trades.py

# Check open positions
python helper_scripts/check_positions.py

# Fix database issues
python helper_scripts/fix_database.py

# Reset database completely
python helper_scripts/reset_database.py
```

### Debugging
```bash
# Check configuration values
python helper_scripts/debug_config.py

# Debug signal generation
python helper_scripts/debug_signals.py

# Check for errors in logs
python helper_scripts/check_errors.py

# Monitor ML training
python helper_scripts/monitor_learning.py
```

### Server Management (Linux/Production)
```bash
# Deploy to server
./helper_scripts/deploy-to-server.sh

# Update bot on server (pull, stop, restart)
./helper_scripts/update_bot.sh

# Manage bot service
./helper_scripts/manage_bot.sh
```

## Configuration

**Main Config** (`trading_bot/config.py`): Central configuration with uppercase constants:
- `API_KEYS`: Exchange API credentials
- `DEFAULT_SETTINGS`: Initial balance, risk per trade, timeframe, paper trading mode
- `INDICATORS`: Technical indicator parameters
- `ML_SETTINGS`: Model hyperparameters and paths
- `RISK_MANAGEMENT`: Stop loss, take profit, position sizing rules
- `STRATEGIES`: Which strategies are enabled and their parameters

**Config Overrides**: Pass custom config dict to `TradingBot(config={...})` to override defaults. See `run_paper_trading.py` for example.

**Enhanced Pipeline Config** (`trader/config.yaml`): Separate YAML config for the Companion Codex pipeline with risk, sizing, signals, and backtest parameters.

## Important Patterns

### Date Handling
Always use `datetime.now(UTC)` instead of `datetime.utcnow()` to avoid deprecation warnings. The codebase was updated from the deprecated method.

### Database Access
NEVER create a new `DatabaseManager()` directly. Always use the singleton:
```python
from trading_bot.database import get_database
db = get_database()
```

### Model Loading
The ML model must exist before starting the bot. `run_paper_trading.py` checks for `models/trading_model.pkl` and exits if missing. Train with `train_comprehensive_model.py` first.

### Portfolio Initialization
Portfolio state is initialized from database on bot startup in `_initialize_portfolio()`. The `reset_portfolio.py` script resets balance to €100 and clears positions/trades in the database.

### Enhanced Pipeline Import
The bot gracefully handles missing enhanced pipeline:
```python
try:
    from trader.data.features import add_features
    ENHANCED_PIPELINE_AVAILABLE = True
except ImportError:
    ENHANCED_PIPELINE_AVAILABLE = False
```

### Path Resolution
Use `config_paths.py` for consistent path resolution across the project. It provides `PROJECT_ROOT` and helper functions to locate data, models, and logs directories.

## Project Structure Notes

- **Root scripts** (`run_paper_trading.py`, `main.py`, `train_comprehensive_model.py`): Entry points for different modes
- **`trading_bot/`**: Main bot implementation with all core logic
- **`trader/`**: Enhanced pipeline with advanced features (data/, signals/, sizing/, risk/, live/, backtest/)
- **`helper_scripts/`**: Developer tools (see helper_scripts/README.md for full list)
- **`data/`**: SQLite database and legacy portfolio_state.json (gitignored)
- **`models/`**: Trained ML models (gitignored)
- **`logs/`**: Log files (gitignored)
- **`test_results/`**: CSV files from backtests (gitignored)

## Paper Trading vs Live Trading

Currently configured for paper trading with €100 starting balance. To switch to live trading:
1. Set `paper_trading: False` in config
2. Add real Kraken API keys to `.env`
3. Understand that real money will be at risk

The bot is optimized for Kraken Pro with aggressive settings (no fees with subscription).

## Critical Files

- `trading_bot/bot.py:52-500` - Main bot logic and trading loop
- `trading_bot/database.py:37-200` - Database schema and operations
- `trading_bot/config.py` - All configuration constants
- `run_paper_trading.py` - Paper trading entry point with €100 config
- `helper_scripts/reset_portfolio.py` - Portfolio reset script (use frequently)
