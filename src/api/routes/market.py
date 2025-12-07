"""API routes for market data"""

from fastapi import APIRouter, Query
from alpaca.data.timeframe import TimeFrame
from src.agent import agent

router = APIRouter()

# Timeframe mapping for API parameter conversion
TIMEFRAME_MAP = {
    "1Min": TimeFrame.Minute,
    "5Min": TimeFrame(5, "Min"),
    "15Min": TimeFrame(15, "Min"),
    "1H": TimeFrame.Hour,
    "1D": TimeFrame.Day
}


@router.get("/bars/{symbol}")
def get_bars(
    symbol: str,
    timeframe: str = Query("1Min", description="1Min, 5Min, 15Min, 1H, or 1D"),
    limit: int = Query(100, description="Number of bars to retrieve")
):
    """Get historical price bars for a symbol"""
    tf = TIMEFRAME_MAP.get(timeframe, TimeFrame.Minute)
    return agent.get_historical_bars(symbol, timeframe=tf, limit=limit)