"""API routes for order management"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.agent import agent

router = APIRouter()


class OrderRequest(BaseModel):
    """Request model for submitting orders"""
    symbol: str = Field(..., description="Stock ticker symbol")
    qty: float = Field(..., gt=0, description="Quantity to trade")
    side: str = Field(..., description="BUY or SELL")
    order_type: str = Field("market", description="market or limit")
    limit_price: Optional[float] = Field(None, description="Limit price (required for limit orders)")


@router.get("/")
def get_all_orders():
    """Get all orders (open, filled, and canceled)"""
    return agent.get_orders()


@router.post("/submit")
def submit_order(req: OrderRequest):
    """Submit a new market or limit order"""
    side = req.side.upper()

    if req.order_type == "market":
        if side == "BUY":
            return agent.market_buy(req.symbol, req.qty)
        elif side == "SELL":
            return agent.market_sell(req.symbol, req.qty)
        else:
            raise HTTPException(status_code=400, detail="Invalid side, must be BUY or SELL")

    elif req.order_type == "limit":
        if not req.limit_price:
            raise HTTPException(status_code=400, detail="limit_price is required for limit orders")
        return agent.limit_order(
            req.symbol,
            req.qty,
            req.limit_price,
            side=side
        )

    raise HTTPException(status_code=400, detail="Unsupported order type")