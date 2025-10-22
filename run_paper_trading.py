#!/usr/bin/env python
"""
Startet den Trading-Bot im Paper Trading Modus mit 100€ Startkapital.
"""

import sys
from pathlib import Path


# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from trading_bot.bot import TradingBot
from trading_bot.database import get_database


def check_model_exists() -> bool:
    """Prüft, ob das KI-Modell trainiert wurde."""
    model_path = project_root / 'models' / 'trading_model.pkl'
    return model_path.exists()


def run():
    """Konfiguriert und startet den Bot für das Paper Trading."""
    
    if not check_model_exists():
        print("❌ FEHLER: KI-Modell nicht gefunden!")
        print("Bitte trainieren Sie zuerst das Modell mit einem der folgenden Befehle:")
        print("   python train_comprehensive_model.py")
        sys.exit(1)
    
    # Stelle sicher, dass die Datenbank existiert, bevor der Bot startet.
    # get_database() initialisiert die DB und erstellt die Datei, falls sie fehlt.
    get_database('trading_bot.db')
    
    # Spezifische Konfiguration für das 100€-Experiment
    paper_trading_config = {
        'settings': {
            'initial_balance': 100.0,
            'paper_trading': True,
            'use_enhanced_pipeline': False, # Einfache ML-Strategie für den Anfang
        },
        'strategies': {
            'ml_based': {'enabled': True, 'min_confidence': 0.70},
            'trend_following': {'enabled': False},
            'mean_reversion': {'enabled': False},
        }
    }

    # Bot initialisieren und starten
    bot = TradingBot(config=paper_trading_config)
    bot.run(symbols=['BTC/EUR', 'ETH/EUR'])

if __name__ == "__main__":
    run()