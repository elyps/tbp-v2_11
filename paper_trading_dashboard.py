"""
Kompaktes Live-Dashboard für das Paper Trading Experiment.
Zeigt die wichtigsten Kennzahlen für das 100€-Startkapital.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add trading_bot to path
sys.path.insert(0, str(Path(__file__).parent))

from trading_bot.database import get_database

# ANSI Farben
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'

def clear_screen():
    """Löscht den Bildschirm."""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_currency(value: float, color: bool = False) -> str:
    """Formatiert Währungswerte."""
    formatted = f"€{value:,.2f}"
    if color:
        if value > 0:
            return f"{Colors.GREEN}{formatted}{Colors.RESET}"
        elif value < 0:
            return f"{Colors.RED}{formatted}{Colors.RESET}"
    return formatted

def print_dashboard(db, start_capital):
    """Druckt das Dashboard."""
    clear_screen()

    # Daten holen
    portfolio = db.get_portfolio()
    stats = db.get_trade_statistics()
    positions = db.get_all_positions()
    recent_trades = db.get_trades(status='closed', limit=5)

    # Header
    print(f"{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║     🚀 PAPER TRADING DASHBOARD (100€ Challenge) 🚀    ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"\n  {Colors.YELLOW}Letzte Aktualisierung:{Colors.RESET} {datetime.now().strftime('%H:%M:%S')}\n")

    # --- Performance ---
    if portfolio:
        # Lese das aktuelle Kapital aus der DB, aber nutze das Skript-Kapital als Fallback
        # Wenn die DB leer war und der Bot neu startet, kann der Wert fehlen.
        # Wir verwenden daher das im Skript definierte Kapital als verlässliche Quelle.
        equity = portfolio.get('equity', start_capital)
    else:
        equity = start_capital

    pnl = equity - start_capital
    pnl_percent = (pnl / start_capital) * 100 if start_capital > 0 else 0.0
    pnl_str = format_currency(pnl, color=True)
    pnl_percent_str = f"({pnl_percent:+.2f}%)"

    print(f"  {Colors.BOLD}PERFORMANCE{Colors.RESET}")
    print(f"  ├─ Startkapital:      {format_currency(start_capital)}")
    print(f"  ├─ Aktuelles Kapital:   {Colors.BOLD}{format_currency(equity)}{Colors.RESET}")
    print(f"  └─ Gewinn / Verlust:    {pnl_str} {pnl_percent_str}")
    print()

    # --- Trade-Statistiken ---
    total_trades = stats.get('total_trades', 0)
    win_rate = stats.get('win_rate', 0.0)

    print(f"  {Colors.BOLD}STATISTIKEN (geschlossene Trades){Colors.RESET}")
    print(f"  ├─ Trades gesamt:       {total_trades}")
    print(f"  ├─ Gewinn-Trades:       {Colors.GREEN}{stats.get('winning_trades', 0)}{Colors.RESET}")
    print(f"  ├─ Verlust-Trades:      {Colors.RED}{stats.get('losing_trades', 0)}{Colors.RESET}")
    print(f"  └─ Win-Rate:            {Colors.BOLD}{win_rate:.1f}%{Colors.RESET}")
    print()

    # --- Offene Positionen ---
    print(f"  {Colors.BOLD}OFFENE POSITIONEN ({len(positions)}){Colors.RESET}")
    if positions:
        for pos in positions:
            pnl_pos = pos.get('pnl', 0.0)
            pnl_pos_str = format_currency(pnl_pos, color=True)
            print(f"  ├─ {pos['symbol']:<10} | Menge: {pos['amount']:.4f} | P&L: {pnl_pos_str}")
    else:
        print("  └─ Keine offenen Positionen.")
    print()

    # --- Letzte geschlossene Trades ---
    print(f"  {Colors.BOLD}LETZTE TRADES{Colors.RESET}")
    if recent_trades:
        for trade in recent_trades:
            pnl_trade = trade.get('pnl', 0.0)
            pnl_trade_str = format_currency(pnl_trade, color=True)
            action_color = Colors.GREEN if trade['action'] == 'buy' else Colors.RED
            print(f"  └─ {trade['timestamp'][11:19]} | {action_color}{trade['action'].upper():<4}{Colors.RESET} {trade['symbol']:<10} | P&L: {pnl_trade_str}")
    else:
        print("  └─ Noch keine geschlossenen Trades.")
    print()

    print(f"{Colors.YELLOW}Drücke STRG+C zum Beenden.{Colors.RESET}")


def main():
    """Hauptfunktion für das Dashboard."""
    start_capital = 100.0
    db_path = 'trading_bot.db'

    if not Path(db_path).exists():
        print(f"Datenbank '{db_path}' nicht gefunden.")
        print("Bitte starte zuerst den Bot mit 'python run_paper_trading.py'.")
        sys.exit(1)

    db = get_database(db_path)
    print("Verbinde mit Datenbank... Dashboard startet.")
    time.sleep(1)

    try:
        while True:
            print_dashboard(db, start_capital)
            time.sleep(5)  # Alle 5 Sekunden aktualisieren
    except KeyboardInterrupt:
        print("\n\nDashboard beendet.")
        db.close()
    except Exception as e:
        print(f"\nEin Fehler ist aufgetreten: {e}")
        db.close()


if __name__ == "__main__":
    main()