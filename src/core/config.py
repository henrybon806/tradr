"""Configuration management"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """API configuration from environment variables"""
    
    # News API
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    NEWSAPI_BASE_URL = "https://newsapi.org/v2"
    
    # Stock Prices
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    
    FINNHUB_KEY = os.getenv("FINNHUB_KEY")
    FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
    
    POLYGON_KEY = os.getenv("POLYGON_KEY")
    POLYGON_BASE_URL = "https://api.polygon.io/v1"
    
    # AI Models
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    #Trading API Keys
    ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
    ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET")
