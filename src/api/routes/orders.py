from fastapi import APIRouter
from pydantic import BaseModel
from src.agent import agent

router = APIRouter()

class OrderRequest(BaseModel):
    symbol: str
    qty: float
    side: str  # BUY or SELL
    order_type: str = "market"
    limit_price: float | None = None

@router.get("/")
def get_all_orders():
    return agent.get_orders()

@router.post("/submit")
def submit_order(req: OrderRequest):
    side = req.side.upper()

    if req.order_type == "market":
        return agent.market_buy(req.symbol, req.qty) if side == "BUY" else agent.market_sell(req.symbol, req.qty)

    if req.order_type == "limit":
        return agent.limit_order(
            req.symbol,
            req.qty,
            req.limit_price,
            side=side
        )

    return {"error": "Unsupported order type"}