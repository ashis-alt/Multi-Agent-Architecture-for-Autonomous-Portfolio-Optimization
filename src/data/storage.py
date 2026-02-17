import sqlite3
from datetime import datetime
from termcolor import colored

DB_PATH = "portfolio.db"

def init_db():
    """Initializes the SQLite database with required tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Trade History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ticker TEXT,
                action TEXT,
                quantity REAL,
                price REAL,
                pnl REAL DEFAULT 0.0,
                reasoning TEXT
            )
        ''')
        
        # 2. Lessons Table (Episodic Memory)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ticker TEXT,
                lesson_text TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(colored("--- 💾 Database Initialized (portfolio.db) ---", "cyan"))
    except Exception as e:
        print(colored(f"Database Error: {e}", "red"))

def log_trade(ticker, action, qty, price, reason):
    """Saves a executed trade to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO trades (timestamp, ticker, action, quantity, price, reasoning)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, ticker, action, qty, price, reason))
        
        conn.commit()
        conn.close()
        print(colored(f"📝 Trade logged to DB: {action} {qty} {ticker}", "green"))
    except Exception as e:
        print(colored(f"Failed to log trade: {e}", "red"))

def get_recent_trades(limit=5):
    """Retrieves the last N trades."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trades ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows