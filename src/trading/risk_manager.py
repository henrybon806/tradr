from src.data.news.news_fetcher import NewsFetcher


class RiskManager():
    def __init__(self):
        self.recent_news = []
        self.news_fetcher = NewsFetcher()
    
    def start(self):
        while True:
            break
    
    def check_news(self):
        self.recent_news = self.news_fetcher.fetch_trending_news()
        print(self.recent_news)
        
    def analyze_news(self):
        