"""SQLite database for tracking trades and holdings"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "tradr.db"

def init_db():
    """Create database tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Trades table - stores individual buy batches (each purchase is a separate row)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date_bought TIMESTAMP,
            price_at_purchase REAL NOT NULL,
            quantity INTEGER NOT NULL,
            date_sold TIMESTAMP,
            sold BOOLEAN DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            cash REAL NOT NULL
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO balance (id, cash) VALUES (1, 0)")
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def buy(symbol: str, quantity: int, price: float) -> None:
    """Record a buy trade - creates a new batch entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert new buy batch
    cursor.execute("""
        INSERT INTO trades (symbol, date_bought, price_at_purchase, quantity, sold)
        VALUES (?, ?, ?, ?, 0)
    """, (symbol, datetime.now(), price, quantity))
    
    # Deduct from cash balance
    cursor.execute("UPDATE balance SET cash = cash - ?", (quantity * price,))
    conn.commit()
    conn.close()
    
    print(f"BUY {quantity} {symbol} @ ${price}")

def sell(symbol: str, quantity: int, price: float) -> None:
    """Record a sell trade - sells from oldest batches first (FIFO)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get unsold batches for this symbol, ordered by date (FIFO)
    cursor.execute("""
        SELECT id, quantity FROM trades 
        WHERE symbol = ? AND sold = 0
        ORDER BY date_bought ASC
    """, (symbol,))
    batches = cursor.fetchall()
    
    remaining_to_sell = quantity
    
    # Sell from oldest batches first
    for batch_id, batch_quantity in batches:
        if remaining_to_sell <= 0:
            break
        
        if batch_quantity <= remaining_to_sell:
            # Sell entire batch
            cursor.execute("""
                UPDATE trades 
                SET sold = 1, date_sold = ?
                WHERE id = ?
            """, (datetime.now(), batch_id))
            remaining_to_sell -= batch_quantity
        else:
            # Partial sell - split the batch
            cursor.execute("""
                UPDATE trades 
                SET quantity = ?
                WHERE id = ?
            """, (batch_quantity - remaining_to_sell, batch_id))
            
            # Insert sold portion
            cursor.execute("""
                SELECT price_at_purchase FROM trades WHERE id = ?
            """, (batch_id,))
            original_price = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO trades (symbol, date_bought, price_at_purchase, quantity, date_sold, sold)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (symbol, cursor.execute("SELECT date_bought FROM trades WHERE id = ?", (batch_id,)).fetchone()[0], 
                  original_price, remaining_to_sell, datetime.now()))
            
            remaining_to_sell = 0
    
    # Add proceeds to cash
    cursor.execute("UPDATE balance SET cash = cash + ?", (quantity * price,))
    conn.commit()
    conn.close()
    
    print(f"SELL {quantity} {symbol} @ ${price}")

def add_trade(symbol: str, action: str, quantity: int, price: float) -> None:
    """Add a buy/sell trade (deprecated - use buy() or sell() instead)"""
    if action.lower() == "buy":
        buy(symbol, quantity, price)
    elif action.lower() == "sell":
        sell(symbol, quantity, price)

def get_all_trades() -> list:
    """Get all trades (current and closed positions)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, symbol, date_bought, price_at_purchase, quantity, date_sold, sold
        FROM trades
        ORDER BY date_bought
    """)
    trades = cursor.fetchall()
    conn.close()
    
    return trades

def get_holdings() -> list:
    """Get all current holdings (unsold batches only)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, symbol, date_bought, price_at_purchase, quantity
        FROM trades 
        WHERE sold = ?
        ORDER BY symbol, date_bought
    """, (False,))
    holdings = cursor.fetchall()
    conn.close()
    
    return holdings

def get_liquidity() -> float:
    """Gets the current liquidity available to buy"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT cash FROM balance WHERE id = 1")
    (cash,) = cursor.fetchone()

    conn.close()
    return cash

def set_balance(amount: float) -> None:
    """Set the cash balance to a specific amount"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE balance SET cash = ? WHERE id = 1", (amount,))
    conn.commit()
    conn.close()
    
    print(f"Balance set to ${amount:.2f}")

if __name__ == "__main__":
    init_db()