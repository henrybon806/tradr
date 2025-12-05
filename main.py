from fastapi import FastAPI
from src.trading.client import TraderClient
from src.api.routes import account, orders, positions, market
from fastapi.middleware.cors import CORSMiddleware

agent = TraderClient()

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