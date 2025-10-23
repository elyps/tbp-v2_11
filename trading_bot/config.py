"""
Konfigurationsdatei für den Trading-Bot
"""

# API-Schlüssel für Kraken (sollten in Produktion in Umgebungsvariablen gespeichert werden)
import os
from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()

API_KEYS = {
    'kraken': {
        'api_key': os.getenv('KRAKEN_API_KEY', 'YOUR_KRAKEN_API_KEY'),
        'api_secret': os.getenv('KRAKEN_API_SECRET', 'YOUR_KRAKEN_API_SECRET')
    },
    'newsapi_key': os.getenv('NEWSAPI_KEY', ''),
    'cryptocompare_key': os.getenv('CRYPTOCOMPARE_KEY', ''),
    'coindesk_key': os.getenv('COINDESK_API_KEY', ''),  # CoinDesk API für Krypto-News
}

# Standardwerte für das Trading
DEFAULT_SETTINGS = {
    'timeframe': '1h',  # Standard-Zeitrahmen für die Analyse (1h = aktiver, 4h = mittel, 1d = langfristig)
    'initial_balance': 100.0,  # Startkapital in EUR (1000€ für bessere Position-Größen)
    'risk_per_trade': 1.0,  # Risiko pro Trade in % des Kontoguthabens
    'max_drawdown': 20.0,  # Maximaler Drawdown in %
    'trading_fee': 0.1,  # Handelsgebühr in %
    'slippage': 0.05,  # Erwarteter Slippage in %
    'paper_trading': True,  # Paper Trading aktiviert (kein echtes Geld)
    'use_enhanced_pipeline': True,  # Verwende neue Companion Codex Pipeline
    'continuous_learning': True,
    'enable_historical_import': True,  # Historische Daten importieren
    'historical_import_interval_hours': 168,  # Wöchentlich (7 Tage)
    'min_samples_retrain': 100,
    'retrain_frequency_hours': 24,
    # AI Learning Settings
    'enable_news_learning': True,  # Lernt aus News-Sentiment
    'enable_market_learning': True,  # Lernt aus Marktdaten
    'news_fetch_interval_hours': 4,  # Hole News alle 4 Stunden
    'market_data_fetch_interval_hours': 1,  # Hole Marktdaten jede Stunde
    'auto_retrain': True,  # Automatisches Retraining
}

# Standard-Indikatoren und ihre Parameter
INDICATORS = {
    'sma': [20, 50, 200],
    'ema': [9, 21, 50],
    'rsi': 14,
    'macd': {'fast': 12, 'slow': 26, 'signal': 9},
    'bollinger_bands': {'window': 20, 'std_dev': 2},
    'atr': 14,
}

# KI-Modell-Einstellungen (XGBoost - Best für Trading)
ML_SETTINGS = {
    'model_type': 'xgboost',  # 'xgboost', 'lightgbm', 'random_forest', 'gradient_boosting'
    'model_path': 'models/',
    'n_estimators': 200,
    'max_depth': 7,
    'learning_rate': 0.05,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'train_test_split': 0.8,
    'sequence_length': 60,  # Anzahl der vergangenen Kerzen für die Vorhersage
    'prediction_length': 5,  # Anzahl der vorherzusagenden Kerzen
    'validation_split': 0.1,
}

# Risikomanagement (AGGRESSIV für viele Trades - Kraken Pro Abo ohne Gebühren)
RISK_MANAGEMENT = {
    'max_risk_per_trade': 0.02,  # 2% des Kapitals pro Trade (aggressive Positionsgröße)
    'max_portfolio_risk': 0.08,  # 8% des Gesamtportfolios (mehr parallel Trading)
    'max_open_positions': 5,  # BIS ZU 5 Positionen gleichzeitig (Multi-Markt Trading)
    'min_risk_reward_ratio': 1.5,  # Min 1.5:1 Risk-Reward (auch kleine Gewinne mitnehmen)
    'min_confidence': 0.65,  # 65% Mindest-Konfidenz (nur verlässliche Signale)
    'stop_loss_pct': 0.015,  # Stop-Loss 1.5% (moderater Schutz)
    'take_profit_pct': 0.025,  # Take-Profit 2.5% (kleinere Gewinne früher realisieren)
    'trailing_stop': True,
    'trailing_stop_distance': 0.005,  # Trailing Stop 0.5% (folgt Gewinn)
    'partial_take_profit': True,  # Gewinne teilweise sichern
    'partial_tp_pct': 0.015,  # Bei 1.5% bereits 50% der Position schließen (schnell)
    'min_profit_target_eur': 2.0,
}

# Strategie-Einstellungen (Kraken-optimiert)
STRATEGIES = {
    'trend_following': {
        'enabled': True,
        'timeframes': ['1h', '4h', '1d'],
        'indicators': ['sma', 'macd', 'rsi'],
    },
    'mean_reversion': {
        'enabled': True,  # Aktiviert für Kraken
        'timeframes': ['15m', '1h'],
        'indicators': ['bollinger_bands', 'rsi'],
    },
    'breakout': {
        'enabled': True,
        'timeframes': ['1h', '4h'],
        'indicators': ['atr', 'volume'],
    },
    'ml_based': {
        'enabled': False,  # ❌ DEAKTIVIERT: Modell muss erst trainiert werden (verhindert automatische SOL-Käufe)
        'min_confidence': 0.65,
        'timeframes': ['1h', '4h'],
    },
}

# Logging-Konfiguration
LOGGING_CONFIG = {
    'level': 'DEBUG',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/trading_bot.log'
}
