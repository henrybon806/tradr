from fastapi import FastAPI
from src.api.routes import account, orders, positions, market, database
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import time
from datetime import datetime

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
app.include_router(database.router, prefix="/database")

@app.get("/")
def root():
    return {"message": "Trading API is running"}

def run_trading_logic_once():
    try:
        print(f"\n{'='*60}")
        print(f"Trading Logic Execution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        risk_manager = RiskManager()
        
        print("1. Analyzing news...")
        predictions = risk_manager.analyze_news()
        print(f"   Found predictions for {len(predictions)} symbols")
        
        print("2. Generating trading signals...")
        signals = risk_manager.analyze_all_holdings_with_news(predictions)
        
        print("3. Creating allocation plan...")
        allocation_plan = risk_manager.generate_cash_allocation_plan(signals)
        print(f"   Plan: {allocation_plan.get('summary', 'No summary')}")
        
        if allocation_plan.get("num_actions", 0) > 0:
            print("4. Executing allocation plan...")
            execution_result = risk_manager.trader.execute_allocation_plan(allocation_plan)
            print(f"   Success: {execution_result.get('summary', 'No summary')}")
        else:
            print("4. No actions to execute (all signals neutral/hold)")
        
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n❌ Trading logic error: {e}")

def run_trading_logic_loop():
    hour_in_seconds = 3600
    
    run_trading_logic_once()
    
    while True:
        print(f"Next trading logic execution in 1 hour ({datetime.now().strftime('%H:%M:%S')} + 1h)")
        time.sleep(hour_in_seconds)
        run_trading_logic_once()

if __name__ == "__main__":
    port = 8000
    
    # Start trading logic in background thread (runs every hour)
    trading_thread = threading.Thread(target=run_trading_logic_loop, daemon=True)
    trading_thread.start()
    
    # Start API server (blocking)
    print(f"Starting Trading API on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
