"""
AI Learning Engine - Kontinuierliches Lernsystem mit Multi-Source Daten
Sammelt Daten aus News, Trades, Marktdaten und trainiert das Modell automatisch
"""

import logging
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from threading import Thread, Event

# UTC import with fallback for older Python versions
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

logger = logging.getLogger(__name__)


class CoinDeskAPI:
    """CoinDesk API Client für Krypto-News"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.coindesk.com/pf/api/v3/content/fetch"

    def get_crypto_news(self, limit: int = 20) -> List[Dict]:
        """Holt aktuelle Krypto-News von CoinDesk"""
        try:
            # CoinDesk API verwendet GraphQL-ähnliche Queries
            params = {
                'query': json.dumps({
                    'size': limit,
                    'from': 0,
                    'offset': 0
                }),
                'filter': json.dumps({
                    'type': 'story',
                    'taxonomy.primary_tag.name': 'Markets'
                })
            }

            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                articles = []

                for item in data.get('content_elements', [])[:limit]:
                    article = {
                        'title': item.get('headlines', {}).get('basic', ''),
                        'description': item.get('description', {}).get('basic', ''),
                        'url': item.get('website_url', ''),
                        'publishedAt': item.get('publish_date', ''),
                        'source': 'CoinDesk',
                        'content': item.get('content_elements', [{}])[0].get('content', '') if item.get('content_elements') else ''
                    }
                    articles.append(article)

                logger.info(f"CoinDesk: {len(articles)} Artikel abgerufen")
                return articles
            else:
                logger.warning(f"CoinDesk API Fehler: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Fehler beim Abrufen von CoinDesk News: {e}")
            return []


class AILearningEngine:
    """
    Hauptklasse für kontinuierliches KI-Lernen
    Sammelt Daten aus mehreren Quellen und trainiert das Modell
    """

    def __init__(self, bot, config: Dict):
        """
        Args:
            bot: TradingBot Instanz
            config: Konfiguration mit API Keys und Einstellungen
        """
        self.bot = bot
        self.config = config
        self.db = bot.db

        # API Clients
        self.coindesk = CoinDeskAPI(config['api_keys'].get('coindesk_key'))

        # Scheduler
        self.stop_event = Event()
        self.scheduler_thread = None

        # Learning Stats
        self.stats = {
            'total_news_processed': 0,
            'total_market_data_collected': 0,
            'last_news_fetch': None,
            'last_market_fetch': None,
            'last_retrain': None,
            'model_accuracy_history': []
        }

        # Lade Stats aus DB
        self._load_stats()

        logger.info("AI Learning Engine initialisiert")

    def start(self):
        """Startet den Lern-Scheduler"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Learning Engine läuft bereits")
            return

        self.stop_event.clear()
        self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info("✓ AI Learning Engine gestartet (läuft im Hintergrund)")

    def stop(self):
        """Stoppt den Lern-Scheduler"""
        self.stop_event.set()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("AI Learning Engine gestoppt")

    def _scheduler_loop(self):
        """Haupt-Scheduler-Loop"""
        logger.info("AI Learning Scheduler gestartet")

        news_interval = self.config['settings'].get('news_fetch_interval_hours', 4) * 3600
        market_interval = self.config['settings'].get('market_data_fetch_interval_hours', 1) * 3600
        retrain_interval = self.config['settings'].get('retrain_frequency_hours', 24) * 3600

        last_news = time.time()
        last_market = time.time()
        last_retrain = time.time()

        while not self.stop_event.is_set():
            try:
                current_time = time.time()

                # News-Sammlung
                if self.config['settings'].get('enable_news_learning') and \
                   (current_time - last_news) >= news_interval:
                    logger.info("🗞️  Sammle News-Daten...")
                    self._collect_news_data()
                    last_news = current_time
                    self.stats['last_news_fetch'] = datetime.now(UTC).isoformat()

                # Marktdaten-Sammlung
                if self.config['settings'].get('enable_market_learning') and \
                   (current_time - last_market) >= market_interval:
                    logger.info("📊 Sammle Marktdaten...")
                    self._collect_market_data()
                    last_market = current_time
                    self.stats['last_market_fetch'] = datetime.now(UTC).isoformat()

                # Auto-Retraining
                if self.config['settings'].get('auto_retrain') and \
                   (current_time - last_retrain) >= retrain_interval:
                    logger.info("🧠 Starte automatisches Retraining...")
                    self._auto_retrain()
                    last_retrain = current_time
                    self.stats['last_retrain'] = datetime.now(UTC).isoformat()

                self._save_stats()

            except Exception as e:
                logger.error(f"Fehler im Learning Scheduler: {e}", exc_info=True)

            # Sleep in kleinen Schritten für schnelles Stop-Response
            for _ in range(60):  # 60 Sekunden = 1 Minute
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def _collect_news_data(self):
        """Sammelt News von allen Quellen"""
        all_news = []

        # 1. CoinDesk
        try:
            coindesk_news = self.coindesk.get_crypto_news(limit=20)
            all_news.extend(coindesk_news)
        except Exception as e:
            logger.error(f"CoinDesk Fehler: {e}")

        # 2. NewsAPI (über NewsProvider)
        try:
            if hasattr(self.bot, 'news_provider') and self.bot.news_provider:
                newsapi_news = self.bot.news_provider.get_crypto_news('BTC', limit=20)
                all_news.extend(newsapi_news)
        except Exception as e:
            logger.error(f"NewsAPI Fehler: {e}")

        # 3. CryptoCompare
        try:
            if hasattr(self.bot, 'news_provider') and self.bot.news_provider:
                cc_news = self.bot.news_provider._fetch_cryptocompare_news('BTC')
                all_news.extend(cc_news)
        except Exception as e:
            logger.error(f"CryptoCompare Fehler: {e}")

        # Verarbeite und speichere News
        if all_news:
            self._process_and_store_news(all_news)
            self.stats['total_news_processed'] += len(all_news)
            logger.info(f"✓ {len(all_news)} News-Artikel gesammelt und verarbeitet")

    def _process_and_store_news(self, news_articles: List[Dict]):
        """Verarbeitet News und speichert in DB"""
        for article in news_articles:
            try:
                # Sentiment-Analyse
                sentiment_score = self._analyze_sentiment(
                    article.get('title', '') + ' ' + article.get('description', '')
                )

                # Speichere in DB
                self.db.save_news({
                    'symbol': 'BTC',  # Hauptwährung
                    'title': article.get('title', '')[:500],
                    'description': article.get('description', '')[:1000],
                    'url': article.get('url', ''),
                    'source': article.get('source', 'unknown'),
                    'published_at': article.get('publishedAt', datetime.now(UTC).isoformat()),
                    'sentiment_score': sentiment_score,
                    'sentiment_label': self._get_sentiment_label(sentiment_score)
                })

            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten von News: {e}")

    def _analyze_sentiment(self, text: str) -> float:
        """Einfache Sentiment-Analyse"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity  # -1 bis +1
        except:
            # Fallback: Keyword-basiert
            positive_words = ['bullish', 'surge', 'rally', 'gain', 'rise', 'profit', 'positive', 'up', 'high']
            negative_words = ['bearish', 'crash', 'fall', 'loss', 'drop', 'negative', 'down', 'low', 'risk']

            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)

            if pos_count + neg_count == 0:
                return 0.0
            return (pos_count - neg_count) / (pos_count + neg_count)

    def _get_sentiment_label(self, score: float) -> str:
        """Konvertiert Sentiment-Score zu Label"""
        if score > 0.2:
            return 'positive'
        elif score < -0.2:
            return 'negative'
        else:
            return 'neutral'

    def _collect_market_data(self):
        """Sammelt Marktdaten von Kraken"""
        symbols = ['BTC/USD', 'ETH/USD', 'BTC/EUR', 'ETH/EUR']

        for symbol in symbols:
            try:
                # Hole aktuelle Marktdaten
                df = self.bot.data_provider.get_historical_data(
                    symbol=symbol,
                    timeframe='1h',
                    limit=24  # Letzte 24 Stunden
                )

                if df is not None and not df.empty:
                    # Berechne Features
                    df_with_indicators = self.bot.indicators.calculate_all(df)

                    # Erstelle Training-Sample
                    self._create_training_samples(df_with_indicators, symbol)

                    self.stats['total_market_data_collected'] += len(df)
                    logger.debug(f"✓ {len(df)} Kerzen für {symbol} gesammelt")

            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Marktdaten für {symbol}: {e}")

    def _create_training_samples(self, df: pd.DataFrame, symbol: str):
        """Erstellt Training-Samples aus Marktdaten"""
        try:
            # Hole News-Sentiment für Symbol
            news_sentiment = self._get_recent_news_sentiment(symbol)

            # Erstelle Label: Preis in 1h höher/niedriger?
            df['future_return'] = df['close'].pct_change(1).shift(-1)
            df['label'] = (df['future_return'] > 0.001).astype(int) + 1  # 0=Down, 1=Neutral, 2=Up

            # Speichere jede Zeile als Training-Sample
            for idx in range(len(df) - 1):
                row = df.iloc[idx]

                if pd.isna(row['label']):
                    continue

                features = self._extract_features(row, news_sentiment)

                self.db.save_training_data({
                    'symbol': symbol,
                    'timestamp': row.name.isoformat() if hasattr(row.name, 'isoformat') else str(row.name),
                    'features': json.dumps({k: float(v) if isinstance(v, (int, float, np.number)) else str(v)
                                          for k, v in features.items()}),
                    'label': int(row['label']),
                    'future_return': float(row['future_return']),
                    'news_sentiment': news_sentiment
                })

        except Exception as e:
            logger.error(f"Fehler beim Erstellen von Training-Samples: {e}")

    def _extract_features(self, row: pd.Series, news_sentiment: float) -> Dict:
        """Extrahiert Features aus einer Datenzeile"""
        features = {}

        # Technische Indikatoren
        for col in row.index:
            if col not in ['label', 'future_return', 'timestamp']:
                try:
                    val = row[col]
                    if not pd.isna(val):
                        features[col] = float(val)
                except:
                    pass

        # News-Sentiment hinzufügen
        features['news_sentiment'] = news_sentiment

        return features

    def _get_recent_news_sentiment(self, symbol: str) -> float:
        """Holt durchschnittliches News-Sentiment der letzten 24h"""
        try:
            # Hole News aus DB (letzte 24h)
            news = self.db.get_recent_news(symbol, hours=24)

            if not news:
                return 0.0

            sentiments = [n.get('sentiment_score', 0.0) for n in news]
            return float(np.mean(sentiments))

        except Exception as e:
            logger.error(f"Fehler beim Abrufen von News-Sentiment: {e}")
            return 0.0

    def _auto_retrain(self):
        """Automatisches Retraining des Modells"""
        try:
            # Hole Training-Daten aus DB
            training_samples = self.db.get_training_data(limit=10000)

            min_samples = self.config['settings'].get('min_samples_retrain', 100)

            if len(training_samples) < min_samples:
                logger.info(f"Nicht genug Samples für Retraining ({len(training_samples)}/{min_samples})")
                return

            logger.info(f"🧠 Starte Retraining mit {len(training_samples)} Samples...")

            # Konvertiere zu DataFrame
            df_samples = pd.DataFrame(training_samples)

            # Extrahiere Features und Labels
            X = []
            y = []

            for idx, row in df_samples.iterrows():
                try:
                    features = json.loads(row['features'])
                    X.append(list(features.values()))
                    y.append(int(row['label']))
                except Exception as e:
                    logger.error(f"Fehler beim Parsen von Sample {idx}: {e}")
                    continue

            if len(X) < min_samples:
                logger.warning("Nicht genug valide Samples")
                return

            # Konvertiere zu NumPy
            X = np.array(X)
            y = np.array(y)

            # Trainiere Modell
            logger.info(f"Training mit {len(X)} Samples, {X.shape[1]} Features...")

            # Verwende das ML-Modell des Bots
            X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
            y_series = pd.Series(y)

            self.bot.ml_model.train(X_df, y_series)

            # Evaluiere
            predictions = self.bot.ml_model.predict(X_df)
            accuracy = (predictions['prediction'] == y_series).mean()

            self.stats['model_accuracy_history'].append({
                'timestamp': datetime.now(UTC).isoformat(),
                'accuracy': float(accuracy),
                'samples': len(X)
            })

            logger.info(f"✓ Retraining abgeschlossen - Accuracy: {accuracy:.2%}")

            # Speichere Performance
            self.db.save_model_performance({
                'timestamp': datetime.now(UTC).isoformat(),
                'accuracy': float(accuracy),
                'samples_used': len(X),
                'features_count': X.shape[1]
            })

        except Exception as e:
            logger.error(f"Fehler beim Auto-Retraining: {e}", exc_info=True)

    def _load_stats(self):
        """Lädt Learning-Stats aus DB"""
        try:
            # Implementierung abhängig von DB-Struktur
            pass
        except:
            pass

    def _save_stats(self):
        """Speichert Learning-Stats in DB"""
        try:
            # Implementierung abhängig von DB-Struktur
            pass
        except:
            pass

    def get_stats(self) -> Dict:
        """Gibt aktuelle Learning-Stats zurück"""
        return self.stats.copy()
