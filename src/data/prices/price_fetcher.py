"""Main stock price data fetcher

Functions:
- get_current_price(symbol)
- get_historical_prices(symbol, interval)
- get_intraday_prices(symbol)
"""

import requests
from src.core.config import Config

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
    
    def prepare_analysis_dataset(self, trader, news_predictions: dict, discovery_symbols: list = None):
        """
        Collects all external data needed for RiskManager’s analysis.
        This function ONLY fetches data — it performs NO analysis.

        Returns a dict:

        {
            "portfolio": {
                "AAPL": {"history": <daily_history>},
                "TSLA": {"history": <daily_history>},
                ...
            },
            "news_only": {
                "NVDA": {"history": <daily_history>},
                ...
            },
            "discovery": {
                "IBM": {"history": <daily_history>},
                ...
            }
        }
        """

        dataset = {
            "portfolio": {},
            "news_only": {},
            "discovery": {}
        }

        positions = trader.get_positions()
        portfolio_symbols = [p["symbol"] for p in positions]

        for symbol in portfolio_symbols:
            history = self.get_daily_prices_alpha_vantage(symbol)
            dataset["portfolio"][symbol] = {"history": history}

        for symbol in news_predictions.keys():
            if symbol not in portfolio_symbols:
                history = self.get_daily_prices_alpha_vantage(symbol)
                dataset["news_only"][symbol] = {"history": history}
                
        discovery_symbols = discovery_symbols or []

        for symbol in discovery_symbols:
            if (
                symbol not in portfolio_symbols and
                symbol not in news_predictions
            ):
                history = self.get_daily_prices_alpha_vantage(symbol)
                dataset["discovery"][symbol] = {"history": history}

        return dataset
