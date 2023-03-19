import yfinance as yf
import numpy as np
from typing import List, Dict, Callable


class Stock:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_stock_data(self, start: str, end: str, interval: str):
        return yf.download(self.symbol, start=start, end=end, interval=interval)


class Trade:
    def __init__(self, symbol: str, price: float, action: str):
        self.symbol = symbol
        self.price = price
        self.action = action


class Portfolio:
    def __init__(self, cash: float):
        self.cash = cash
        self.trades: List[Trade] = []

    def buy(self, symbol: str, price: float):
        self.trades.append(Trade(symbol, price, "buy"))
        self.cash -= price

    def sell(self, symbol: str, price: float):
        self.trades.append(Trade(symbol, price, "sell"))
        self.cash += price

    def value(self) -> float:
        value = self.cash
        for trade in self.trades:
            value += trade.price if trade.action == "buy" else -trade.price
        return value

    def positions(self) -> Dict[str, int]:
        positions = {}
        for trade in self.trades:
            if trade.symbol not in positions:
                positions[trade.symbol] = 0
            positions[trade.symbol] += 1 if trade.action == "buy" else -1
        return positions

    def total_allocation(self) -> Dict[str, float]:
        return {
            symbol: (shares * self.value())
            for symbol, shares in self.positions().items()
        }


class Backtester:
    def __init__(
        self, targets: Dict[str, float], start_date: str, end_date: str, interval: str
    ):
        self.targets = targets
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.stocks = {symbol: Stock(symbol) for symbol in targets.keys()}

    def backtest(
        self, starting_amount: float, buy_fn: Callable, sell_fn: Callable
    ) -> Tuple[float, List[float]]:
        portfolio = Portfolio(starting_amount)
        daily_returns = []
        prev_value = starting_amount

        for date in self.stocks[next(iter(self.stocks))].data.index:
            for symbol, stock in self.stocks.items():
                stock_data = stock.get_stock_data(
                    self.start_date, self.end_date, self.interval
                )
                stock_price = stock_data.loc[:date, "Open"][-1]

                if sell_fn(stock_data, portfolio):
                    portfolio.sell(symbol, stock_price)
                elif stock_price < portfolio.cash and buy_fn(stock_data, portfolio):
                    portfolio.buy(symbol, stock_price)

            # Calculate daily returns and append to the list
            current_value = portfolio.value()
            daily_returns.append((current_value - prev_value) / prev_value)
            prev_value = current_value

        return current_value, daily_returns
