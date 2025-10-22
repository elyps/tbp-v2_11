"""
AI Learning Dashboard - Zeigt Lernfortschritt und Modell-Performance
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.database import get_database
from config_paths import DB_PATH

# ANSI Farben
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'

def clear_screen():
    """Löscht den Bildschirm."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_dashboard(db):
    """Druckt das AI Learning Dashboard."""
    clear_screen()

    # Header
    print(f"{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║          🧠  AI LEARNING DASHBOARD - Live Performance  🧠          ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"\n  {Colors.YELLOW}Letzte Aktualisierung:{Colors.RESET} {datetime.now().strftime('%H:%M:%S')}\n")

    # --- Model Performance ---
    print(f"  {Colors.BOLD}{Colors.MAGENTA}📊 MODEL PERFORMANCE{Colors.RESET}")

    perf_history = db.get_model_performance_history(limit=10)

    if perf_history:
        latest = perf_history[0]

        accuracy = latest.get('accuracy', 0.0) * 100
        samples = latest.get('samples_count', 0)
        timestamp = latest.get('timestamp', '')

        # Farbige Accuracy
        if accuracy >= 70:
            acc_color = Colors.GREEN
        elif accuracy >= 60:
            acc_color = Colors.YELLOW
        else:
            acc_color = Colors.RED

        print(f"  ├─ Aktuelle Accuracy:    {acc_color}{accuracy:.1f}%{Colors.RESET}")
        print(f"  ├─ Training Samples:     {samples:,}")
        print(f"  ├─ Letztes Training:     {timestamp[:16] if timestamp else 'N/A'}")

        # Trend anzeigen (Vergleich mit vorherigem)
        if len(perf_history) > 1:
            prev_accuracy = perf_history[1].get('accuracy', 0.0) * 100
            diff = accuracy - prev_accuracy
            trend = "📈" if diff > 0 else "📉" if diff < 0 else "━"
            trend_color = Colors.GREEN if diff > 0 else Colors.RED if diff < 0 else Colors.YELLOW
            print(f"  └─ Trend:                {trend} {trend_color}{diff:+.1f}%{Colors.RESET}")
        else:
            print(f"  └─ Trend:                ━ (Nicht genug Daten)")
    else:
        print(f"  {Colors.YELLOW}└─ Noch keine Modell-Performance-Daten verfügbar{Colors.RESET}")

    print()

    # --- Training Data Stats ---
    print(f"  {Colors.BOLD}{Colors.MAGENTA}📚 TRAINING DATEN{Colors.RESET}")

    try:
        df_training = db.get_training_data(limit=100000)
        total_samples = len(df_training)

        if total_samples > 0:
            # Zähle Labels
            labels = df_training['label'].value_counts().to_dict() if 'label' in df_training.columns else {}

            print(f"  ├─ Total Samples:        {total_samples:,}")

            if labels:
                print(f"  ├─ Verkauf (0):          {labels.get(0, 0):,}")
                print(f"  ├─ Halten (1):           {labels.get(1, 0):,}")
                print(f"  └─ Kauf (2):             {labels.get(2, 0):,}")
            else:
                print(f"  └─ Labels:               Noch keine")
        else:
            print(f"  {Colors.YELLOW}└─ Noch keine Training-Daten gesammelt{Colors.RESET}")

    except Exception as e:
        print(f"  {Colors.RED}└─ Fehler beim Laden: {str(e)}{Colors.RESET}")

    print()

    # --- News Stats ---
    print(f"  {Colors.BOLD}{Colors.MAGENTA}📰 NEWS & SENTIMENT{Colors.RESET}")

    try:
        news_24h = db.get_recent_news('BTC', limit=1000, hours=24)
        news_total = len(news_24h)

        if news_total > 0:
            # Durchschnittliches Sentiment
            sentiments = [n.get('sentiment_score', 0.0) for n in news_24h]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

            # Sentiment-Verteilung
            positive = sum(1 for s in sentiments if s > 0.2)
            negative = sum(1 for s in sentiments if s < -0.2)
            neutral = news_total - positive - negative

            # Farbiges Sentiment
            if avg_sentiment > 0.2:
                sent_color = Colors.GREEN
                sent_label = "Positiv"
            elif avg_sentiment < -0.2:
                sent_color = Colors.RED
                sent_label = "Negativ"
            else:
                sent_color = Colors.YELLOW
                sent_label = "Neutral"

            print(f"  ├─ News (24h):           {news_total:,}")
            print(f"  ├─ Ø Sentiment:          {sent_color}{avg_sentiment:+.2f} ({sent_label}){Colors.RESET}")
            print(f"  ├─ Positiv:              {Colors.GREEN}{positive}{Colors.RESET}")
            print(f"  ├─ Neutral:              {Colors.YELLOW}{neutral}{Colors.RESET}")
            print(f"  └─ Negativ:              {Colors.RED}{negative}{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}└─ Keine News in den letzten 24h{Colors.RESET}")

    except Exception as e:
        print(f"  {Colors.RED}└─ Fehler: {str(e)}{Colors.RESET}")

    print()

    # --- Learning Progress ---
    print(f"  {Colors.BOLD}{Colors.MAGENTA}📈 LERNFORTSCHRITT (Letzte 5 Trainings){Colors.RESET}")

    if perf_history and len(perf_history) > 1:
        print(f"  ┌──────────────────┬───────────┬──────────────┐")
        print(f"  │ Zeitpunkt        │ Accuracy  │ Samples      │")
        print(f"  ├──────────────────┼───────────┼──────────────┤")

        for i, perf in enumerate(perf_history[:5]):
            timestamp = perf.get('timestamp', '')[:16] if perf.get('timestamp') else 'N/A'
            accuracy = perf.get('accuracy', 0.0) * 100
            samples = perf.get('samples_count', 0)

            # Farbe basierend auf Accuracy
            if accuracy >= 70:
                color = Colors.GREEN
            elif accuracy >= 60:
                color = Colors.YELLOW
            else:
                color = Colors.RED

            print(f"  │ {timestamp:<16} │ {color}{accuracy:6.1f}%{Colors.RESET}  │ {samples:>10,}   │")

        print(f"  └──────────────────┴───────────┴──────────────┘")
    else:
        print(f"  {Colors.YELLOW}└─ Noch nicht genug Trainings für Verlauf{Colors.RESET}")

    print()

    # --- System Status ---
    print(f"  {Colors.BOLD}{Colors.MAGENTA}⚙️  SYSTEM STATUS{Colors.RESET}")

    # Prüfe ob Bot läuft
    try:
        # Hole letzte Trade-Aktivität
        recent_trades = db.get_trades(limit=1)

        if recent_trades:
            last_trade_time = recent_trades[0].get('timestamp', '')
            if last_trade_time:
                try:
                    last_trade_dt = datetime.fromisoformat(last_trade_time.replace('Z', '+00:00'))
                    time_diff = datetime.now() - last_trade_dt.replace(tzinfo=None)

                    if time_diff.total_seconds() < 3600:  # Letzte Stunde
                        status = f"{Colors.GREEN}Aktiv ✓{Colors.RESET}"
                    elif time_diff.total_seconds() < 86400:  # Letzte 24h
                        status = f"{Colors.YELLOW}Inaktiv (>1h){Colors.RESET}"
                    else:
                        status = f"{Colors.RED}Gestoppt (>24h){Colors.RESET}"
                except:
                    status = f"{Colors.YELLOW}Unbekannt{Colors.RESET}"
            else:
                status = f"{Colors.YELLOW}Unbekannt{Colors.RESET}"
        else:
            status = f"{Colors.YELLOW}Keine Trades{Colors.RESET}"

        print(f"  ├─ Bot Status:           {status}")

    except:
        print(f"  ├─ Bot Status:           {Colors.YELLOW}Unbekannt{Colors.RESET}")

    # Datenbank-Info
    db_size = Path(DB_PATH).stat().st_size / (1024 * 1024) if Path(DB_PATH).exists() else 0
    print(f"  └─ DB Größe:             {db_size:.1f} MB")

    print()
    print(f"  {Colors.CYAN}Drücke STRG+C zum Beenden{Colors.RESET}")
    print()


def main():
    """Hauptfunktion"""
    db_path = DB_PATH

    if not db_path.exists():
        print(f"Datenbank nicht gefunden: {db_path}")
        print("Bitte starte zuerst den Bot mit 'python run_paper_trading.py'.")
        sys.exit(1)

    db = get_database(str(db_path))
    print("Verbinde mit Datenbank... AI Learning Dashboard startet.")
    time.sleep(1)

    try:
        while True:
            print_dashboard(db)
            time.sleep(5)  # Update alle 5 Sekunden
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Dashboard beendet.{Colors.RESET}\n")
        db.close()


if __name__ == "__main__":
    main()
