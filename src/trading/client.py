from src.core.config import Config
from src.database import simple_db
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data import StockHistoricalDataClient, StockLatestTradeRequest
from alpaca.data.requests import StockBarsRequest
from alpaca.trading.requests import GetPortfolioHistoryRequest
from alpaca.data.timeframe import TimeFrame

class TraderClient:
    def __init__(self):
        self.db = simple_db
        self.portfolio = {}

        self.trading_client = TradingClient(
            Config.ALPACA_API_KEY,
            Config.ALPACA_API_SECRET,
            paper=True
        )

        self.data_client = StockHistoricalDataClient(
            Config.ALPACA_API_KEY,
            Config.ALPACA_API_SECRET
        )

    # -----------------------------
    # ORDER EXECUTION
    # -----------------------------

    def market_buy(self, symbol, qty):
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        return self.trading_client.submit_order(order)

    def market_sell(self, symbol, qty):
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        return self.trading_client.submit_order(order)

    def limit_order(self, symbol, qty, limit_price, side=OrderSide.BUY):
        order = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            limit_price=limit_price,
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        return self.trading_client.submit_order(order)

    def cancel_order(self, order_id):
        return self.trading_client.cancel_order_by_id(order_id)

    # -----------------------------
    # ACCOUNT + PORTFOLIO DATA
    # -----------------------------

    def get_account(self):
        """Returns dict so dashboard JSON can consume easily."""
        acc = self.trading_client.get_account()
        return {
            "cash": float(acc.cash),
            "equity": float(acc.equity),
            "portfolio_value": float(acc.portfolio_value),
            "buying_power": float(acc.buying_power),
            "multiplier": acc.multiplier,
            "status": acc.status,
            "daytrade_count": acc.daytrade_count,
        }

    def get_current_balance(self):
        """Dashboard main display value."""
        acc = self.trading_client.get_account()
        return float(acc.cash)

    def get_positions(self):
        positions = self.trading_client.get_all_positions()
        output = []
        for p in positions:
            output.append({
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_entry_price": float(p.avg_entry_price),
                "market_value": float(p.market_value),
                "current_price": float(p.current_price),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": float(p.unrealized_plpc),
                "side": p.side,
            })
        return output

    def get_orders(self, status="all"):
        orders = self.trading_client.get_orders(status=status)
        output = []
        for o in orders:
            output.append({
                "id": o.id,
                "symbol": o.symbol,
                "qty": float(o.qty),
                "filled_qty": float(o.filled_qty),
                "side": o.side,
                "type": o.type,
                "status": o.status,
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "submitted_at": str(o.submitted_at),
                "filled_at": str(o.filled_at) if o.filled_at else None,
            })
        return output
    
    def get_portfolio_history(self, period="1M", timeframe="1D", extended_hours=False):
        req = GetPortfolioHistoryRequest(
            period=period,
            timeframe=timeframe,
            extended_hours=extended_hours
        )

        history = self.trading_client.get_portfolio_history(req)

        # Format the response into JSON-friendly dicts
        return {
            "timestamp": history.timestamp,          # UNIX timestamps
            "equity": history.equity,                # portfolio equity values
            "profit_loss": history.profit_loss,      # profit/loss in dollars
            "profit_loss_pct": history.profit_loss_pct,  # percent change
            "base_value": history.base_value,
            "timeframe": timeframe,
            "period": period
        }

    # -----------------------------
    # MARKET DATA (for dashboard charts)
    # -----------------------------

    def get_latest_price(self, symbol):
        """For real-time price tiles on dashboard."""
        req = StockLatestTradeRequest(symbol_or_symbols=symbol)
        res = self.data_client.get_stock_latest_trade(req)
        return float(res[symbol].price)

    def get_historical_bars(self, symbol, timeframe=TimeFrame.Minute, limit=100):
        """For charting in dashboard."""
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            limit=limit
        )
        bars = self.data_client.get_stock_bars(req)
        output = []
        for bar in bars[symbol]:
            output.append({
                "timestamp": bar.timestamp.isoformat(),
                "open": float(bar.open),
                "high": float(bar.high),
                "low": float(bar.low),
                "close": float(bar.close),
                "volume": int(bar.volume)
            })
        return output