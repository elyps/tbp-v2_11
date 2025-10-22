"""
Zentrale Pfad-Konfiguration für das Trading Bot Projekt.
Alle Skripte sollten diese Pfade verwenden.
"""
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).parent

# Data Directory
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = DATA_DIR / 'trading_bot.db'
PORTFOLIO_STATE_PATH = DATA_DIR / 'portfolio_state.json'

# Test Results
TEST_RESULTS_DIR = PROJECT_ROOT / 'test_results'
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Logs
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Models
MODELS_DIR = PROJECT_ROOT / 'models'
MODELS_DIR.mkdir(exist_ok=True)

# News Data
NEWS_DATA_DIR = PROJECT_ROOT / 'news_data'
NEWS_DATA_DIR.mkdir(exist_ok=True)

# Helper für String-Pfade (Kompatibilität)
def get_db_path() -> str:
    """Gibt DB-Pfad als String zurück."""
    return str(DB_PATH)

def get_portfolio_state_path() -> str:
    """Gibt Portfolio-State-Pfad als String zurück."""
    return str(PORTFOLIO_STATE_PATH)
