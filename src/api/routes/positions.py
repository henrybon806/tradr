from fastapi import APIRouter
from src.trading.client import TraderClient

router = APIRouter()
agent = TraderClient()

@router.get("/")
def get_positions():
    return agent.get_positions()