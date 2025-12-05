from fastapi import APIRouter, Query
from main import agent

router = APIRouter()

@router.get("/")
def get_account():
    return agent.get_account()

@router.get("/balance")
def get_balance():
    return {"balance": agent.get_current_balance()}

@router.get("/history")
def get_account_history(
    period: str = Query("1M", description="1D, 1W, 1M, 3M, 6M, 1A, ALL"),
    timeframe: str = Query("1D", description="1Min, 5Min, 15Min, 1H, 1D"),
    extended_hours: bool = Query(True)
):
    return agent.get_portfolio_history(
        period=period,
        timeframe=timeframe,
        extended_hours=extended_hours
    )