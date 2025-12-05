from fastapi import FastAPI
from src.api.routes import account, orders, positions, market
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

from src.trading.risk_manager import RiskManager

app = FastAPI(
    title="Trading Engine API",
    version="0.1"
)

origins = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include route groups
app.include_router(account.router, prefix="/account")
app.include_router(orders.router, prefix="/orders")
app.include_router(positions.router, prefix="/positions")
app.include_router(market.router, prefix="/market")

@app.get("/")
def root():
    return {"message": "Trading API is running"}

def run_trading_logic():
    """Your trading code runs here in background thread"""
    risk_manager = RiskManager()
    # risk_manager.check_news()

if __name__ == "__main__":
    port = 8000
    
    # Start trading logic in background thread
    trading_thread = threading.Thread(target=run_trading_logic, daemon=True)
    trading_thread.start()
    
    # Start API server (blocking)
    uvicorn.run(app, host="0.0.0.0", port=port)
