"""Main news data fetcher

Functions:
- fetch_news_by_symbol(symbol)
- fetch_news_by_query(query)
- fetch_trending_news()
"""

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ...core.config import Config

class NewsFetcher:
    """Fetch financial news from NewsAPI"""
    
    def __init__(self):
        self.api_key = Config.NEWSAPI_KEY
        self.base_url = Config.NEWSAPI_BASE_URL
    
    def fetch_news(self, symbol: str, limit: int = 10):
        """Fetch for stock news"""
        url = f"{self.base_url}/everything"
        params = {
            "q": symbol,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "apiKey": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def fetch_trending_news(self, limit: int = 10):
        """Fetch top headlines"""
        url = f"{self.base_url}/top-headlines"
        params = {
            "category": "business",
            "pageSize": limit,
            "apiKey": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()
