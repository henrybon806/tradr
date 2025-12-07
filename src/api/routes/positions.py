"""API routes for portfolio positions"""

from fastapi import APIRouter
from src.agent import agent

router = APIRouter()


@router.get("/")
def get_positions():
    """Get all current positions"""
    return agent.get_positions()