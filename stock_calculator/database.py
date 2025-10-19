import os
import sys
import sqlite3

# Get the directory where this file lives
if getattr(sys, 'frozen', False):
    # Running as an .exe
    base_dir = os.path.dirname(sys.executable)
else:
    # Running from source
    base_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(base_dir, "stocks.db")

def init_db():
    """Create local database file if not existing."""
    os.makedirs(base_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            buy_price REAL,
            shares INTEGER,
            break_even REAL
        )
    """)

    # Sold stocks history
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            buy_price REAL,
            shares INTEGER,
            break_even REAL,
            sell_price REAL,
            profit_loss REAL,
            date_sold TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_stock(ticker, buy_price, shares, break_even):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO stocks (ticker, buy_price, shares, break_even) VALUES (?, ?, ?, ?)",
        (ticker.upper(), buy_price, shares, break_even)
    )
    conn.commit()
    conn.close()

def get_all_stocks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, ticker, buy_price, shares, break_even FROM stocks")
    rows = c.fetchall()
    conn.close()
    return rows

def get_db_path():
    """Optional: return database file path."""
    return DB_PATH

def move_to_history(stock_id: int, sell_shares: int, sell_price: float, profit_loss: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT ticker, buy_price, shares, break_even FROM stocks WHERE id=?", (stock_id,))
    stock = cursor.fetchone()
    if stock:
        ticker, buy_price, shares, break_even = stock

        # Insert into history
        cursor.execute("""
            INSERT INTO history (ticker, buy_price, shares, break_even, sell_price, profit_loss)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, buy_price, sell_shares, break_even, sell_price, profit_loss))

        # Update remaining shares or delete
        remaining_shares = shares - sell_shares
        if remaining_shares > 0:
            cursor.execute("UPDATE stocks SET shares=? WHERE id=?", (remaining_shares, stock_id))
        else:
            cursor.execute("DELETE FROM stocks WHERE id=?", (stock_id,))

        conn.commit()
    conn.close()



def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY date_sold DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
