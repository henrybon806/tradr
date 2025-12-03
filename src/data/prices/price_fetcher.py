"""Main stock price data fetcher

Functions:
- get_current_price(symbol)
- get_historical_prices(symbol, interval)
- get_intraday_prices(symbol)
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ...core.config import Config

class PriceFetcher:
    """Fetch stock prices from various providers"""
    
    def __init__(self):
        self.alpha_vantage_key = Config.ALPHA_VANTAGE_KEY
        self.finnhub_key = Config.FINNHUB_KEY
        self.polygon_key = Config.POLYGON_KEY
    
    def get_current_price_alpha_vantage(self, symbol: str):
        """Get current price from Alpha Vantage"""
        url = Config.ALPHA_VANTAGE_BASE_URL
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_intraday_prices_alpha_vantage(self, symbol: str, interval: str = "5min"):
        """Get intraday prices from Alpha Vantage"""
        url = Config.ALPHA_VANTAGE_BASE_URL
        params = {
            "function": "INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": self.alpha_vantage_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_daily_prices_alpha_vantage(self, symbol: str):
        """Get daily prices from Alpha Vantage"""
        url = Config.ALPHA_VANTAGE_BASE_URL
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.alpha_vantage_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_current_price_finnhub(self, symbol: str):
        """Get current price from Finnhub"""
        url = f"{Config.FINNHUB_BASE_URL}/quote"
        params = {
            "symbol": symbol,
            "token": self.finnhub_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_historical_finnhub(self, symbol: str, resolution: str = "D", days: int = 7):
        """Get historical prices from Finnhub"""
        from datetime import datetime, timedelta
        
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        url = f"{Config.FINNHUB_BASE_URL}/stock/candle"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": start_time,
            "to": end_time,
            "token": self.finnhub_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_current_price_polygon(self, symbol: str):
        """Get current price from Polygon"""
        url = f"{Config.POLYGON_BASE_URL}/last/quote/{symbol}"
        params = {
            "apiKey": self.polygon_key
        }
        response = requests.get(url, params=params)
        return response.json()
