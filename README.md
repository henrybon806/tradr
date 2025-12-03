# Tradr - AI Trading Bot

A framework for fetching real-time financial news and stock price data.

## Project Structure

```
src/
├── core/                    # Configuration
│   └── config.py           # API keys and base URLs
│
└── data/                   # Data fetching layer
    ├── providers/          # API provider implementations
    │   ├── news_providers.py
    │   └── price_providers.py
    │
    ├── news/              # News fetching
    │   └── news_fetcher.py
    │
    └── prices/            # Stock price fetching
        └── price_fetcher.py
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Supported Data Sources

### News
- NewsAPI.org

### Stock Prices
- Alpha Vantage
- Finnhub
- Polygon.io
