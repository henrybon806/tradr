"""Base class for all API data fetchers"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException


class BaseAPIFetcher(ABC):
    """Base class for API data fetchers with common HTTP functionality"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling
        
        Args:
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters
            method: HTTP method (GET, POST, etc.)
            
        Returns:
            JSON response as dictionary
            
        Raises:
            RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except RequestException as e:
            print(f"Request failed for {url}: {e}")
            raise
    
    def __del__(self):
        """Clean up session on deletion"""
        if hasattr(self, 'session'):
            self.session.close()
