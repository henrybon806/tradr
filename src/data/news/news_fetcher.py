"""Financial news data fetcher"""

from typing import Dict, Any
from src.core.config import Config
from src.data.base_fetcher import BaseAPIFetcher


class NewsFetcher(BaseAPIFetcher):
    """Fetch financial news from NewsAPI"""
    
    def __init__(self):
        super().__init__(
            api_key=Config.NEWSAPI_KEY,
            base_url=Config.NEWSAPI_BASE_URL
        )
    
    def fetch_news(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch news for a specific stock symbol
        
        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of articles to retrieve
            
        Returns:
            Dictionary containing news articles
        """
        params = {
            "q": symbol,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "apiKey": self.api_key
        }
        return self._make_request("/everything", params=params)
    
    def fetch_trending_news(self, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch top business headlines
        
        Args:
            limit: Maximum number of articles to retrieve
            
        Returns:
            Dictionary containing news articles
        """
        params = {
            "category": "business",
            "pageSize": limit,
            "apiKey": self.api_key
        }
        return self._make_request("/top-headlines", params=params)

