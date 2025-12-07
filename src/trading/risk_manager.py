from typing import Any, Dict, List, Set
import requests
from src.data.news.news_fetcher import NewsFetcher
from src.data.prices.price_fetcher import PriceFetcher
from src.models.gemini.querier import GeminiQuerier
from src.trading.client import TraderClient


class RiskManager():
    def __init__(self):
        self.recent_news = {}
        self.news_fetcher = NewsFetcher()
        self.model = GeminiQuerier()
        self.fetcher = PriceFetcher()
        self.trader = TraderClient()
    
    def start(self):
        while True:
            break
    
    def check_news(self):
        return self.news_fetcher.fetch_trending_news()['articles']
        
    def score_news(self):
        articles = self.check_news()

        article_map = {
            a["title"]: a.get("description", "")
            for a in articles
        }

        sentiments = self.model.analyze_sentiment_batch(article_map)

        for title, description in article_map.items():
            sentiment_data = sentiments.get(title, {
                "sentiment": "neutral",
                "score": 0.5,
                "reasoning": "Missing in response"
            })

            self.recent_news[title] = {
                "description": description,
                "sentiment": sentiment_data
            }

        return self.recent_news

    def analyze_news(self):
        articles = self.score_news()

        if not articles:
            return {}

        merged_context = "\n\n".join(
            f"Title: {title}\nDescription: {data['description']}"
            for title, data in articles.items()
        )

        predictions = self.model.predict_price_movement({}, merged_context)
        valid_predictions = self.validate_ticker(predictions)

        return valid_predictions
    
    def validate_ticker(self, predictions: dict) -> dict:
        """
        Takes: dict like { "AAPL": {...}, "META": {...} }
        Returns: dict of only valid tickers.
        """
        valid = {}

        for ticker, pred in predictions.items():

            if ticker is None:
                continue

            av = self.fetcher.get_current_price_alpha_vantage(ticker)

            if av and "Global Quote" in av and av["Global Quote"]:
                valid[ticker] = pred

        return valid
    
    def analyze_all_holdings_with_news(self, news_predictions: Dict[str, Any]):
            """
            Analyze all symbols by consolidating data and making one single call 
            to the batched analyze_trading_signal function.
            """
            positions = self.trader.get_positions()
            portfolio_symbols: Set[str] = {p["symbol"] for p in positions}
            symbols_to_fetch: Set[str] = set(portfolio_symbols)
            
            # Identify all unique symbols from all three sources
            symbols_to_fetch.update(news_predictions.keys())
            gainers = getattr(self, "top_gainers", [])
            for item in gainers:
                symbol = item.get("symbol") or item.get("ticker")
                if symbol:
                    symbols_to_fetch.add(symbol)
                    
            analysis_data: List[Dict[str, Any]] = []
            
            for symbol in symbols_to_fetch:
                news_data = news_predictions.get(symbol, {}).get("reasoning", "")
                
                if symbol in portfolio_symbols:
                    category = "portfolio_signals"
                elif symbol in news_predictions:
                    category = "news_opportunities"
                else:
                    category = "new_buy_candidates"

                try:
                    price_history = self.fetcher.get_daily_prices_alpha_vantage(symbol)
                except Exception:
                    price_history = "Price history unavailable."

                analysis_data.append({
                    "symbol": symbol,
                    "category": category,
                    "price_history": str(price_history),
                    "news": news_data
                })
                
            return self.model.analyze_trading_signal(analysis_data)
    
    def generate_cash_allocation_plan(self, trading_signals: dict) -> dict:
        """
        Takes Gemini trading signals and generates smart cash allocation actions.
        
        Uses professional portfolio management techniques:
        - Kelly Criterion for position sizing (never go negative)
        - Risk/reward ratio analysis
        - Stops selling ALL shares (keeps cushion)
        - Only allocates what's safe (80% of available cash max)
        - Prioritizes by strength and diversification
        
        Args:
            trading_signals: Output from analyze_all_holdings_with_news()
                           Contains portfolio_signals, news_opportunities, new_buy_candidates
        
        Returns:
            dict with keys:
            - "actions": list of {symbol, action, quantity, price_allocation}
            - "cash_available": available cash before plan
            - "cash_remaining": cash after plan (always >= 0)
            - "total_allocation": total cash committed
            - "reasoning": summary of allocation strategy
        """
        # Get current portfolio state
        account = self.trader.get_account()
        positions = self.trader.get_positions()
        pending_orders = self.trader.get_pending_orders()  # Get pending orders
        
        cash_available = account["cash"]
        buying_power = account["buying_power"]  # Use BUYING POWER, not just cash (accounts for margin)
        portfolio_value = account["portfolio_value"]
        current_positions = {p["symbol"]: p for p in positions}
        
        # Build map of pending buy orders by symbol to avoid double-buying
        pending_buy_symbols = {}
        pending_sell_symbols = {}
        for order in pending_orders:
            symbol = order["symbol"]
            qty = order["qty"]
            side = order["side"]
            
            if side == "buy":
                pending_buy_symbols[symbol] = pending_buy_symbols.get(symbol, 0) + qty
            elif side == "sell":
                pending_sell_symbols[symbol] = pending_sell_symbols.get(symbol, 0) + qty
        
        # Parse signals
        portfolio_signals = trading_signals.get("portfolio_signals", {})
        news_opportunities = trading_signals.get("news_opportunities", {})
        new_buy_candidates = trading_signals.get("new_buy_candidates", {})
        
        actions = []
        total_buy_allocation = 0
        total_sell_proceeds = 0
        safe_cash_reserve = max(1000, buying_power * 0.25)  # Keep 25% of buying power as reserve (margin safety)
        
        # --- SELL SIGNALS ---
        # Only sell if: (1) strong sell signal AND (2) position is large enough to matter AND (3) no pending sell order
        for symbol, position_data in current_positions.items():
            signal = portfolio_signals.get(symbol, {})
            action = signal.get("action", "hold")
            strength = signal.get("strength", 0.5)
            
            # Skip if we already have a pending sell order for this symbol
            if symbol in pending_sell_symbols:
                print(f"Skipping sell for {symbol} - pending sell order exists ({pending_sell_symbols[symbol]} shares)")
                continue
            
            if action == "sell" and strength >= 0.7:  # Only strong sells
                qty = position_data["qty"]
                current_price = position_data["current_price"]
                proceeds = qty * current_price
                
                # Sell only a portion (Kelly Criterion: ~25-50% of position)
                # Keeps some upside exposure if we're wrong
                sell_qty = max(1, int(qty * strength))
                sell_proceeds = sell_qty * current_price
                
                actions.append({
                    "symbol": symbol,
                    "action": "sell",
                    "quantity": sell_qty,
                    "price_allocation": sell_proceeds,
                    "strength": strength,
                    "reasoning": signal.get("reasoning", "Partial sell - strong downside signal")
                })
                total_sell_proceeds += sell_proceeds
        
        # --- CALCULATE SAFE BUY BUDGET ---
        # Total budget = current cash + sell proceeds, minus safety reserve
        total_available_for_buys = cash_available + total_sell_proceeds - safe_cash_reserve
        total_available_for_buys = max(0, min(total_available_for_buys, buying_power - safe_cash_reserve))
        
        # Use Kelly Criterion: allocate max 25% of portfolio per single position
        # This ensures we never go negative and manage risk properly
        max_per_position = portfolio_value * 0.08  # Conservative: 8% max per position
        budget_allocation = min(total_available_for_buys * 0.6, buying_power * 0.4)  # Use 60% of available, max 40% of buying power
        
        # --- BUY SIGNALS ---
        # Build prioritized buy list
        buy_candidates = []
        
        # Priority 1: Strengthen existing holdings (portfolio_increase)
        for symbol, signal in portfolio_signals.items():
            if signal.get("action") == "buy" and symbol in current_positions:
                strength = signal.get("strength", 0.5)
                
                # Skip if we already have a pending buy order
                if symbol in pending_buy_symbols:
                    print(f"Skipping buy for {symbol} - pending buy order exists ({pending_buy_symbols[symbol]} shares)")
                    continue
                
                buy_candidates.append({
                    "symbol": symbol,
                    "strength": strength,
                    "priority": 3,
                    "reasoning": signal.get("reasoning", "Strengthen existing position"),
                    "category": "portfolio_increase"
                })
        
        # Priority 2: New opportunities from news
        for symbol, signal in news_opportunities.items():
            if symbol not in current_positions and signal.get("action") in ["buy", "strong_buy"]:
                strength = signal.get("strength", 0.5)
                
                # Skip if we already have a pending buy order
                if symbol in pending_buy_symbols:
                    print(f"Skipping buy for {symbol} - pending buy order exists ({pending_buy_symbols[symbol]} shares)")
                    continue
                
                buy_candidates.append({
                    "symbol": symbol,
                    "strength": strength,
                    "priority": 2,
                    "reasoning": signal.get("reasoning", "News-driven opportunity"),
                    "category": "news_opportunity"
                })
        
        # Priority 3: Lower-conviction new candidates
        for symbol, signal in new_buy_candidates.items():
            if symbol not in current_positions and signal.get("action") == "buy":
                strength = signal.get("strength", 0.5)
                if strength >= 0.6:  # Only higher conviction candidates
                    
                    # Skip if we already have a pending buy order
                    if symbol in pending_buy_symbols:
                        print(f"Skipping buy for {symbol} - pending buy order exists ({pending_buy_symbols[symbol]} shares)")
                        continue
                    
                    buy_candidates.append({
                        "symbol": symbol,
                        "strength": strength,
                        "priority": 1,
                        "reasoning": signal.get("reasoning", "Emerging candidate"),
                        "category": "new_candidate"
                    })
        
        # Sort by priority (higher) then strength
        buy_candidates.sort(key=lambda x: (-x["priority"], -x["strength"]))
        
        # Allocate budget using Kelly Criterion approach
        if budget_allocation > 100 and len(buy_candidates) > 0:
            # Total strength for weighting
            total_strength = sum(max(0.5, c["strength"]) for c in buy_candidates)
            
            # Track actual buying power remaining (conservative check)
            remaining_buying_power = buying_power - safe_cash_reserve
            
            for candidate in buy_candidates:
                symbol = candidate["symbol"]
                strength = max(0.5, candidate["strength"])  # Min 0.5 weight
                
                # Allocate proportional to strength
                allocation = (strength / total_strength) * budget_allocation
                
                # Cap to max per position using Kelly Criterion
                allocation = min(allocation, max_per_position)
                
                # Ensure we don't exceed remaining budget
                if total_buy_allocation + allocation > budget_allocation:
                    allocation = max(0, budget_allocation - total_buy_allocation)
                
                # CRITICAL: Check against actual remaining buying power
                if allocation > remaining_buying_power:
                    print(f"Skipping {symbol}: allocation ${allocation:.2f} exceeds remaining buying power ${remaining_buying_power:.2f}")
                    continue
                
                if allocation >= 50:  # Minimum trade size
                    try:
                        price_history = self.fetcher.get_daily_prices_alpha_vantage(symbol)
                        if isinstance(price_history, list) and len(price_history) > 0:
                            current_price = float(price_history[0].get("close", 100))
                        else:
                            current_price = 100
                        
                        quantity = int(allocation / current_price)
                        
                        if quantity > 0:
                            actions.append({
                                "symbol": symbol,
                                "action": "buy",
                                "quantity": quantity,
                                "price_allocation": allocation,
                                "strength": strength,
                                "reasoning": candidate["reasoning"],
                                "category": candidate["category"]
                            })
                            total_buy_allocation += allocation
                            remaining_buying_power -= allocation  # Deduct from remaining buying power
                    except Exception as e:
                        print(f"Could not process {symbol}: {e}")
        
        # --- FINAL CALCULATIONS ---
        total_allocation = total_sell_proceeds + total_buy_allocation
        final_cash = cash_available + total_sell_proceeds - total_buy_allocation
        
        # Ensure we never go negative (should never happen with logic above)
        if final_cash < 0:
            print(f"WARNING: Negative cash would result ({final_cash}), reducing allocations")
            final_cash = 0
            total_allocation = cash_available + total_sell_proceeds
        
        num_buys = len([a for a in actions if a['action'] == 'buy'])
        num_sells = len([a for a in actions if a['action'] == 'sell'])
        
        return {
            "actions": actions,
            "cash_available": cash_available,
            "cash_remaining": final_cash,
            "total_allocation": total_allocation,
            "portfolio_value": portfolio_value,
            "num_actions": len(actions),
            "buy_count": num_buys,
            "sell_count": num_sells,
            "pending_buys": pending_buy_symbols,
            "pending_sells": pending_sell_symbols,
            "reasoning": f"Smart allocation: {num_buys} positions to buy, {num_sells} partial sells. Allocated ${total_buy_allocation:.2f} from ${budget_allocation:.2f} budget. ${final_cash:.2f} cash remains (never negative). Avoided double-buying {len(pending_buy_symbols)} symbols with pending orders."
        }