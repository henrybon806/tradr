from fastapi import APIRouter
# from src.agent import agent
from src.agent import agent

router = APIRouter()

@router.get("/")
def get_positions():
    return agent.get_positions()