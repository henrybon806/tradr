from src.data.news.news_fetcher import NewsFetcher
from src.data.prices.price_fetcher import PriceFetcher
from src.database import simple_db

news_fetcher = NewsFetcher()
news = news_fetcher.fetch_news("Top stocks", limit=1)
print(news)

print(simple_db.get_all_trades())