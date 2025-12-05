from fastapi import APIRouter
from main import agent

router = APIRouter()

@router.get("/")
def get_positions():
    return agent.get_positions()