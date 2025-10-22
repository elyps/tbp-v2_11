"""
Database Migration Script
Fügt fehlende Spalten zur bestehenden Datenbank hinzu
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_paths import DB_PATH
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Migriert die Datenbank auf das neueste Schema."""

    if not DB_PATH.exists():
        logger.error(f"Datenbank nicht gefunden: {DB_PATH}")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    logger.info(f"Starte Migration von {DB_PATH}")

    try:
        # Hole aktuelle Spalten der trades-Tabelle
        cursor.execute("PRAGMA table_info(trades)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        logger.info(f"Existierende Spalten in 'trades': {existing_columns}")

        # Prüfe und füge fehlende Spalten hinzu
        migrations = {
            'stop_loss': 'ALTER TABLE trades ADD COLUMN stop_loss REAL',
            'take_profit': 'ALTER TABLE trades ADD COLUMN take_profit REAL',
            'exit_price': 'ALTER TABLE trades ADD COLUMN exit_price REAL',
            'exit_timestamp': 'ALTER TABLE trades ADD COLUMN exit_timestamp TEXT',
            'pnl': 'ALTER TABLE trades ADD COLUMN pnl REAL DEFAULT 0.0',
            'pnl_percent': 'ALTER TABLE trades ADD COLUMN pnl_percent REAL DEFAULT 0.0',
        }

        applied_migrations = 0

        for column, sql in migrations.items():
            if column not in existing_columns:
                logger.info(f"  ✓ Füge Spalte hinzu: {column}")
                cursor.execute(sql)
                applied_migrations += 1
            else:
                logger.info(f"  ⊳ Spalte existiert bereits: {column}")

        conn.commit()

        # Zeige finale Spalten
        cursor.execute("PRAGMA table_info(trades)")
        final_columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"Finale Spalten in 'trades': {final_columns}")

        logger.info(f"✓ Migration abgeschlossen: {applied_migrations} Spalten hinzugefügt")

        # Prüfe training_data Tabelle
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='training_data'
        """)

        if not cursor.fetchone():
            logger.info("Erstelle training_data Tabelle...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT,
                    symbol TEXT NOT NULL,
                    features TEXT,
                    label INTEGER,
                    pnl REAL,
                    timestamp TEXT NOT NULL,
                    future_return REAL,
                    news_sentiment REAL DEFAULT 0.0
                )
            """)
            conn.commit()
            logger.info("✓ training_data Tabelle erstellt")

        # Prüfe news Tabelle
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='news'
        """)

        if not cursor.fetchone():
            logger.info("Erstelle news Tabelle...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    content TEXT,
                    url TEXT,
                    source TEXT,
                    published_at TEXT,
                    sentiment_score REAL DEFAULT 0.0,
                    sentiment_label TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Index für schnelle Queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_symbol ON news(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at)")

            conn.commit()
            logger.info("✓ news Tabelle erstellt")

        # Prüfe model_performance Tabelle
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='model_performance'
        """)

        if not cursor.fetchone():
            logger.info("Erstelle model_performance Tabelle...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_version TEXT,
                    accuracy REAL,
                    precision_score REAL,
                    recall REAL,
                    f1_score REAL,
                    samples_count INTEGER,
                    features_count INTEGER,
                    training_duration REAL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("✓ model_performance Tabelle erstellt")

        conn.close()

        logger.info("=" * 70)
        logger.info("✓ ALLE MIGRATIONEN ERFOLGREICH ABGESCHLOSSEN")
        logger.info("=" * 70)

        return True

    except Exception as e:
        logger.error(f"Fehler bei Migration: {e}", exc_info=True)
        conn.rollback()
        conn.close()
        return False


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
