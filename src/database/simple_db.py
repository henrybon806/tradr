import os
from datetime import datetime
from supabase import create_client, Client
from src.core.config import Config

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", getattr(Config, "SUPABASE_URL", ""))
SUPABASE_KEY = os.getenv("SUPABASE_KEY", getattr(Config, "SUPABASE_KEY", ""))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment or config")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    """Initialize database - tables are created in Supabase console"""
    print(f"Connected to Supabase: {SUPABASE_URL}")
    print("Note: Create 'actions' table in Supabase with: id, timestamp, symbol, action, quantity, strength, reasoning, category, price_allocation, order_id, status")

def save_action(symbol: str, action: str, quantity: int, strength: float, 
                reasoning: str, category: str = None, price_allocation: float = None,
                order_id: str = None, status: str = None) -> int:
    """
    Save an executed allocation action to Supabase.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        action: 'buy' or 'sell'
        quantity: Number of shares
        strength: Signal strength (0.0-1.0)
        reasoning: Why this action was taken
        category: Type of action (portfolio_increase, news_opportunity, new_candidate)
        price_allocation: Dollar amount allocated/spent
        order_id: Alpaca order ID
        status: Order status (filled, pending, etc.)
    
    Returns:
        ID of inserted action
    """
    try:
        data = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "strength": strength,
            "reasoning": reasoning,
            "category": category,
            "price_allocation": price_allocation,
            "order_id": order_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("trades").insert(data).execute()
        
        if response.data:
            return response.data[0]["id"]
        else:
            print(f"Warning: No response from Supabase insert")
            return None
    except Exception as e:
        print(f"Error saving action to Supabase: {e}")
        return None

def get_all_actions(limit: int = None) -> list:
    """
    Get all recorded actions, optionally limited to most recent N.
    
    Returns:
        List of dicts with action data
    """
    try:
        query = supabase.table("trades").select("*").order("timestamp", desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching actions from Supabase: {e}")
        return []

def get_actions_by_symbol(symbol: str) -> list:
    """Get all actions for a specific symbol."""
    try:
        response = supabase.table("trades").select("*").eq("symbol", symbol).order("timestamp", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching actions by symbol from Supabase: {e}")
        return []

def get_actions_by_date(start_date: str = None, end_date: str = None) -> list:
    """Get actions within a date range (format: YYYY-MM-DD)."""
    try:
        query = supabase.table("trades").select("*")
        
        if start_date and end_date:
            query = query.gte("timestamp", f"{start_date}T00:00:00").lte("timestamp", f"{end_date}T23:59:59")
        elif start_date:
            query = query.gte("timestamp", f"{start_date}T00:00:00")
        
        response = query.order("timestamp", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching actions by date from Supabase: {e}")
        return []

def get_action_stats() -> dict:
    """Get summary statistics of all actions."""
    try:
        response = supabase.table("trades").select("*").execute()
        actions = response.data if response.data else []
        
        total_actions = len(actions)
        total_buys = len([a for a in actions if a["action"] == "buy"])
        total_sells = len([a for a in actions if a["action"] == "sell"])
        
        total_shares_bought = sum(a["quantity"] for a in actions if a["action"] == "buy")
        total_shares_sold = sum(a["quantity"] for a in actions if a["action"] == "sell")
        
        total_bought_value = sum(a.get("price_allocation", 0) or 0 for a in actions if a["action"] == "buy")
        total_sold_value = sum(a.get("price_allocation", 0) or 0 for a in actions if a["action"] == "sell")
        
        return {
            "total_actions": total_actions,
            "total_buys": total_buys,
            "total_sells": total_sells,
            "total_shares_bought": total_shares_bought,
            "total_shares_sold": total_shares_sold,
            "total_bought_value": total_bought_value,
            "total_sold_value": total_sold_value,
            "net_capital_deployed": total_bought_value - total_sold_value
        }
    except Exception as e:
        print(f"Error calculating action stats from Supabase: {e}")
        return {
            "total_actions": 0,
            "total_buys": 0,
            "total_sells": 0,
            "total_shares_bought": 0,
            "total_shares_sold": 0,
            "total_bought_value": 0,
            "total_sold_value": 0,
            "net_capital_deployed": 0
        }

if __name__ == "__main__":
    init_db()

