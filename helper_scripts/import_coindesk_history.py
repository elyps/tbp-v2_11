"""
Import Historical Data from CoinDesk
Holt tausende historische News, Preisdaten und erstellt Training-Samples
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import numpy as np
from trading_bot.database import get_database
from trading_bot.data_provider import DataProvider
from trading_bot.indicators import TechnicalIndicators

# UTC import
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc


class CoinDeskHistoricalImporter:
    """
    Holt historische Daten von CoinDesk und erstellt Training-Samples
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.coindesk.com"
        self.api_url = "https://www.coindesk.com/pf/api/v3/content/fetch"
        self.db = get_database()
        self.data_provider = DataProvider(api_keys={}, settings={})
        self.indicators = TechnicalIndicators(config={})

    def fetch_historical_news(self, days_back: int = 30, limit_per_day: int = 50) -> List[Dict]:
        """
        Holt historische News-Artikel von CoinDesk

        Args:
            days_back: Wie viele Tage zurück
            limit_per_day: Maximale Artikel pro Tag
        """
        print(f"\n📰 Hole historische News ({days_back} Tage)...")

        all_articles = []
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days_back)

        # CoinDesk API - Paginiert durch Archive
        offset = 0
        batch_size = 100

        while offset < days_back * limit_per_day:
            try:
                # Query für ältere Artikel
                params = {
                    'query': json.dumps({
                        'size': batch_size,
                        'from': offset,
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
                    self.api_url,
                    params=params,
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('content_elements', [])

                    if not articles:
                        break  # Keine weiteren Artikel

                    for item in articles:
                        published_str = item.get('publish_date', '')
                        if published_str:
                            try:
                                published_dt = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                                if published_dt < start_date:
                                    continue  # Zu alt
                            except:
                                pass

                        article = {
                            'title': item.get('headlines', {}).get('basic', ''),
                            'description': item.get('description', {}).get('basic', ''),
                            'url': item.get('website_url', ''),
                            'publishedAt': published_str,
                            'source': 'CoinDesk',
                            'content': item.get('content_elements', [{}])[0].get('content', '') if item.get('content_elements') else ''
                        }
                        all_articles.append(article)

                    offset += batch_size
                    print(f"  ✓ {len(all_articles)} Artikel bisher...")

                    # Rate Limiting
                    time.sleep(1)

                elif response.status_code == 429:
                    print("  ⏳ Rate Limit - warte 60 Sekunden...")
                    time.sleep(60)
                else:
                    print(f"  ⚠️  API Fehler: {response.status_code}")
                    break

            except Exception as e:
                print(f"  ⚠️  Fehler: {e}")
                break

            # Limit erreicht
            if len(all_articles) >= days_back * limit_per_day:
                break

        print(f"✓ {len(all_articles)} historische News-Artikel gesammelt")
        return all_articles

    def analyze_sentiment(self, text: str) -> float:
        """Einfache Sentiment-Analyse"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            # Fallback: Keyword-basiert
            positive_words = ['bullish', 'surge', 'rally', 'gain', 'rise', 'profit', 'positive', 'up', 'high', 'moon', 'pump']
            negative_words = ['bearish', 'crash', 'fall', 'loss', 'drop', 'negative', 'down', 'low', 'risk', 'dump', 'plunge']

            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)

            if pos_count + neg_count == 0:
                return 0.0
            return (pos_count - neg_count) / (pos_count + neg_count)

    def save_news_to_db(self, articles: List[Dict]):
        """Speichert News in Datenbank"""
        print(f"\n💾 Speichere News in Datenbank...")

        saved_count = 0
        for article in articles:
            try:
                sentiment_score = self.analyze_sentiment(
                    article.get('title', '') + ' ' + article.get('description', '')
                )

                sentiment_label = 'positive' if sentiment_score > 0.2 else 'negative' if sentiment_score < -0.2 else 'neutral'

                self.db.save_news({
                    'symbol': 'BTC',
                    'title': article.get('title', '')[:500],
                    'description': article.get('description', '')[:1000],
                    'url': article.get('url', ''),
                    'source': article.get('source', 'CoinDesk'),
                    'published_at': article.get('publishedAt', datetime.now(UTC).isoformat()),
                    'sentiment_score': sentiment_score,
                    'sentiment_label': sentiment_label
                })
                saved_count += 1

            except Exception as e:
                print(f"  ⚠️  Fehler beim Speichern: {e}")

        print(f"✓ {saved_count} News-Artikel gespeichert")

    def create_training_samples_from_history(self, symbol: str = 'BTC/USD', days_back: int = 30):
        """
        Erstellt Training-Samples aus historischen Markt- und News-Daten

        Args:
            symbol: Trading-Paar (z.B. BTC/USD)
            days_back: Wie viele Tage zurück
        """
        print(f"\n📊 Erstelle Training-Samples für {symbol}...")

        # 1. Hole historische OHLCV Daten
        print("  [1/4] Lade historische Preisdaten...")
        try:
            # Kraken limitiert auf ~720 Kerzen pro Request
            # Für 30 Tage mit 1h Kerzen = 720 Kerzen
            df = self.data_provider.get_historical_data(
                symbol=symbol,
                timeframe='1h',
                limit=min(days_back * 24, 720)
            )

            if df is None or df.empty:
                print("  ❌ Keine Preisdaten verfügbar")
                return 0

            print(f"  ✓ {len(df)} Preisdaten geladen")

        except Exception as e:
            print(f"  ❌ Fehler beim Laden: {e}")
            return 0

        # 2. Berechne technische Indikatoren
        print("  [2/4] Berechne Indikatoren...")
        try:
            df = self.indicators.calculate_all(df)
            print("  ✓ Indikatoren berechnet")
        except Exception as e:
            print(f"  ⚠️  Fehler bei Indikatoren: {e}")

        # 3. Hole News-Sentiment für jeden Zeitpunkt
        print("  [3/4] Lade News-Sentiment...")
        news = self.db.get_recent_news('BTC', limit=10000, hours=days_back * 24)
        print(f"  ✓ {len(news)} News-Artikel verfügbar")

        # Erstelle Sentiment-Zeitreihe
        sentiment_by_time = {}
        for n in news:
            try:
                pub_time = datetime.fromisoformat(n['published_at'].replace('Z', '+00:00'))
                hour_key = pub_time.replace(minute=0, second=0, microsecond=0)
                if hour_key not in sentiment_by_time:
                    sentiment_by_time[hour_key] = []
                sentiment_by_time[hour_key].append(n.get('sentiment_score', 0.0))
            except:
                pass

        # Durchschnitt pro Stunde
        sentiment_avg = {k: np.mean(v) for k, v in sentiment_by_time.items()}

        # 4. Erstelle Training-Samples
        print("  [4/4] Erstelle Training-Samples...")

        # Label: War der Preis in 4h höher/niedriger?
        df['future_return'] = df['close'].pct_change(4).shift(-4)  # 4h voraus
        df['label'] = 1  # Default: HOLD

        # SELL wenn Preis > 1% fällt
        df.loc[df['future_return'] < -0.01, 'label'] = 0

        # BUY wenn Preis > 1% steigt
        df.loc[df['future_return'] > 0.01, 'label'] = 2

        samples_created = 0

        for idx in range(len(df) - 5):  # Letzte 5 überspringen (kein Future-Return)
            row = df.iloc[idx]

            if pd.isna(row['label']) or pd.isna(row['future_return']):
                continue

            # Finde Sentiment für diesen Zeitpunkt
            try:
                row_time = row.name if isinstance(row.name, datetime) else pd.to_datetime(row.name)
                hour_key = row_time.replace(minute=0, second=0, microsecond=0, tzinfo=None)
                news_sentiment = sentiment_avg.get(hour_key, 0.0)
            except:
                news_sentiment = 0.0

            # Features extrahieren
            features = {}
            for col in ['rsi', 'macd', 'sma_20', 'sma_50', 'volume', 'close', 'high', 'low']:
                if col in row.index and not pd.isna(row[col]):
                    features[col] = float(row[col])

            features['news_sentiment'] = news_sentiment
            features['volume_ratio'] = float(row.get('volume', 0) / df['volume'].rolling(20).mean().iloc[idx]) if 'volume' in row.index else 1.0

            # Speichere Training-Sample
            try:
                self.db.save_training_data({
                    'symbol': symbol,
                    'timestamp': row_time.isoformat() if isinstance(row_time, datetime) else str(row_time),
                    'features': json.dumps(features),
                    'label': int(row['label']),
                    'future_return': float(row['future_return']),
                    'news_sentiment': news_sentiment
                })
                samples_created += 1

            except Exception as e:
                print(f"  ⚠️  Sample-Fehler: {e}")

        print(f"✓ {samples_created} Training-Samples erstellt")
        return samples_created


def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("🚀 COINDESK HISTORICAL DATA IMPORT")
    print("=" * 70)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=30, help='Tage zurück (default: 30)')
    parser.add_argument('--symbol', type=str, default='BTC/USD', help='Symbol (default: BTC/USD)')
    parser.add_argument('--skip-news', action='store_true', help='Überspringe News-Import')
    args = parser.parse_args()

    importer = CoinDeskHistoricalImporter()

    # 1. Importiere News
    if not args.skip_news:
        articles = importer.fetch_historical_news(days_back=args.days, limit_per_day=50)
        if articles:
            importer.save_news_to_db(articles)

    # 2. Erstelle Training-Samples
    samples_created = importer.create_training_samples_from_history(
        symbol=args.symbol,
        days_back=args.days
    )

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("✅ IMPORT ABGESCHLOSSEN")
    print("=" * 70)
    print(f"\n📊 Zusammenfassung:")
    print(f"   • {samples_created} Training-Samples erstellt")
    print(f"   • Symbol: {args.symbol}")
    print(f"   • Zeitraum: {args.days} Tage")

    print(f"\n🚀 Nächste Schritte:")
    print(f"   1. Trainiere KI: python helper_scripts/train_now.py")
    print(f"   2. Starte Bot: python run_paper_trading.py")
    print(f"   3. Dashboard: python ai_learning_dashboard.py")
    print()

    importer.db.close()


if __name__ == "__main__":
    main()
