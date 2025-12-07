from fastapi import APIRouter, Query
from typing import Optional, List
from src.database import simple_db

router = APIRouter()

@router.get("/actions")
def get_actions(limit: Optional[int] = Query(100, ge=1, le=1000)):
    """
    Get all recorded trading actions, optionally limited.
    
    Args:
        limit: Maximum number of actions to return (default: 100, max: 1000)
    
    Returns:
        List of action records
    """
    try:
        actions = simple_db.get_all_actions(limit=limit)
        return {
            "success": True,
            "count": len(actions),
            "actions": actions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/actions/symbol/{symbol}")
def get_actions_by_symbol(symbol: str):
    """
    Get all actions for a specific stock symbol.
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL')
    
    Returns:
        List of actions for that symbol
    """
    try:
        symbol = symbol.upper()
        actions = simple_db.get_actions_by_symbol(symbol)
        return {
            "success": True,
            "symbol": symbol,
            "count": len(actions),
            "actions": actions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/actions/date")
def get_actions_by_date(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Get actions within a date range.
    
    Args:
        start_date: Start date in format YYYY-MM-DD
        end_date: End date in format YYYY-MM-DD
    
    Returns:
        List of actions within the date range
    """
    try:
        actions = simple_db.get_actions_by_date(start_date, end_date)
        return {
            "success": True,
            "start_date": start_date,
            "end_date": end_date,
            "count": len(actions),
            "actions": actions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/actions/stats")
def get_action_stats():
    """
    Get summary statistics of all recorded actions.
    
    Returns:
        Dict with aggregated stats (total buys, sells, capital deployed, etc.)
    """
    try:
        stats = simple_db.get_action_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/actions/summary")
def get_actions_summary():
    """
    Get a high-level summary of trading activity.
    
    Returns:
        Summary including action counts, capital info, and top symbols
    """
    try:
        stats = simple_db.get_action_stats()
        recent_actions = simple_db.get_all_actions(limit=10)
        
        # Count actions by symbol
        symbol_counts = {}
        for action in simple_db.get_all_actions(limit=None):
            symbol = action.get("symbol", "UNKNOWN")
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "success": True,
            "summary": {
                "total_actions": stats["total_actions"],
                "total_buys": stats["total_buys"],
                "total_sells": stats["total_sells"],
                "total_capital_deployed": stats["net_capital_deployed"],
                "total_bought_value": stats["total_bought_value"],
                "total_sold_value": stats["total_sold_value"],
                "total_shares_traded": stats["total_shares_bought"] + stats["total_shares_sold"],
                "top_symbols": [{"symbol": s, "action_count": c} for s, c in top_symbols]
            },
            "recent_actions": recent_actions[:5]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/actions/buy-vs-sell")
def get_buy_vs_sell_stats():
    """
    Get comparison of buy vs sell activity.
    
    Returns:
        Breakdown of buy and sell statistics
    """
    try:
        stats = simple_db.get_action_stats()
        
        return {
            "success": True,
            "buy_stats": {
                "total_buys": stats["total_buys"],
                "total_shares": stats["total_shares_bought"],
                "total_value": stats["total_bought_value"],
                "avg_value_per_trade": stats["total_bought_value"] / stats["total_buys"] if stats["total_buys"] > 0 else 0,
                "avg_shares_per_trade": stats["total_shares_bought"] / stats["total_buys"] if stats["total_buys"] > 0 else 0
            },
            "sell_stats": {
                "total_sells": stats["total_sells"],
                "total_shares": stats["total_shares_sold"],
                "total_value": stats["total_sold_value"],
                "avg_value_per_trade": stats["total_sold_value"] / stats["total_sells"] if stats["total_sells"] > 0 else 0,
                "avg_shares_per_trade": stats["total_shares_sold"] / stats["total_sells"] if stats["total_sells"] > 0 else 0
            },
            "net_position": {
                "net_shares": stats["total_shares_bought"] - stats["total_shares_sold"],
                "net_capital": stats["net_capital_deployed"],
                "buy_count": stats["total_buys"],
                "sell_count": stats["total_sells"],
                "ratio": f"{stats['total_buys']}:{stats['total_sells']}"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
