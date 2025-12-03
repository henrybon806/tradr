"""Minimal SQLite database for tracking trades and P&L"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "tradr.db"

def init_db():
    """Create database tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Trades table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profit_loss REAL
        )
    """)
    
    # Portfolio table (current holdings)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            symbol TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL,
            avg_price REAL NOT NULL,
            current_price REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def add_trade(symbol: str, action: str, quantity: int, price: float) -> int:
    """Add a buy/sell trade"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO trades (symbol, action, quantity, price)
        VALUES (?, ?, ?, ?)
    """, (symbol, action, quantity, price))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Trade added: {action.upper()} {quantity} {symbol} @ ${price}")
    return trade_id

def get_all_trades() -> list:
    """Get all trades"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, symbol, action, quantity, price, date FROM trades ORDER BY date")
    trades = cursor.fetchall()
    conn.close()
    
    return trades

def get_current_holdings() -> list:
    """Get current holdings by symbol, calculated from all trades"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all trades ordered by date
    cursor.execute("SELECT symbol, action, quantity, price FROM trades ORDER BY date")
    trades = cursor.fetchall()
    conn.close()
    
    # Calculate holdings by processing trades
    holdings = {}
    for symbol, action, quantity, price in trades:
        if symbol not in holdings:
            holdings[symbol] = {"quantity": 0, "cost_basis": 0}
        
        if action.lower() == "buy":
            holdings[symbol]["quantity"] += quantity
            holdings[symbol]["cost_basis"] += quantity * price
        elif action.lower() == "sell":
            holdings[symbol]["quantity"] -= quantity
            holdings[symbol]["cost_basis"] -= quantity * price
    
    # Convert to list format, excluding zero-quantity positions
    result = []
    for symbol, data in holdings.items():
        if data["quantity"] > 0:
            avg_price = data["cost_basis"] / data["quantity"]
            result.append({
                "symbol": symbol,
                "quantity": data["quantity"],
                "avg_price": avg_price,
                "cost_basis": data["cost_basis"]
            })
    
    return result

if __name__ == "__main__":
    init_db()
