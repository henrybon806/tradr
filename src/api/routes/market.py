from fastapi import APIRouter, Query
from alpaca.data.timeframe import TimeFrame
from main import agent

router = APIRouter()

@router.get("/bars/{symbol}")
def get_bars(
    symbol: str,
    timeframe: str = Query("1Min"), 
    limit: int = Query(100)
):
    # convert timeframe string → Alpaca enum
    tf_map = {
        "1Min": TimeFrame.Minute,
        "5Min": TimeFrame(5, "Min"),
        "15Min": TimeFrame(15, "Min"),
        "1H": TimeFrame.Hour,
        "1D": TimeFrame.Day
    }

    tf = tf_map.get(timeframe, TimeFrame.Minute)

    return agent.get_historical_bars(symbol, timeframe=tf, limit=limit)