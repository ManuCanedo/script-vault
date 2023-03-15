from backtester import Backtester
import random
import math


def calculate_rsi(data):
    delta = data["Adj Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi[-1]


def calculate_sma(data, period=14):
    sma = data["Adj Close"].rolling(window=period).mean()
    return sma[-1]


def calculate_ema(data, period=14):
    ema = data["Adj Close"].ewm(span=period).mean()
    return ema[-1]


def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    short_ema = data["Adj Close"].ewm(span=short_period).mean()
    long_ema = data["Adj Close"].ewm(span=long_period).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_period).mean()
    return macd[-1], signal_line[-1]


def is_buy(stock, data, portfolio) -> bool:
    if len(data) == 0:
        return False

    price = data["Open"][-1]
    rsi = calculate_rsi(data)
    sma = calculate_sma(data)
    ema = calculate_ema(data)
    macd, signal_line = calculate_macd(data)

    if (
        math.isnan(rsi)
        or rsi > 30
        or price > sma
        or price > ema
        or macd < signal_line
    ):
        return False

    mean_buy_price = price if len(portfolio.positions()[stock.symbol]) == 0 else min(portfolio.positions()[stock.symbol])
    current_allocation = portfolio.allocation(stock.symbol)
    target_allocation = backtester.targets.get(stock.symbol, 0)

    portfolio_discount_factor = (mean_buy_price - price) / mean_buy_price
    portfolio_distance_factor = target_allocation - current_allocation

    discount_threshold = 0.05  # Adjust this value according to your risk tolerance
    distance_threshold = max(0.1 * target_allocation, 0.01)

    if (
        portfolio_discount_factor < discount_threshold
        or portfolio_distance_factor < distance_threshold
    ):
        return False

    return True


def is_sell(stock, data, portfolio) -> bool:
    if (
        len(data) == 0
        or stock.symbol not in portfolio.positions()
        or portfolio.positions()[stock.symbol] == 0
    ):
        return False

    price = data["Open"][-1]
    rsi = calculate_rsi(data)
    sma = calculate_sma(data)
    ema = calculate_ema(data)
    macd, signal_line = calculate_macd(data)

    if (
        math.isnan(rsi)
        or rsi < 70
        or price < sma
        or price < ema
        or macd > signal_line
    ):
        return False

    positions = portfolio.positions()
    if not positions:
        return False

    threshold = -(sum(positions.values()) - portfolio.value()) / sum(positions.values())
    if threshold < 0:
        return False

    discount_random = random.random()
    return discount_random < threshold


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    mean_returns = np.mean(returns)
    returns_std = np.std(returns)
    sharpe_ratio = (mean_returns - risk_free_rate) / returns_std
    return sharpe_ratio


if __name__ == "__main__":
    start_date = "2022-01-01"
    end_date = "2023-03-01"
    stocks = {"BRK-B": 0.7, "TSLA": 0.3}
    capital = 10000
    interval = "1d"

    # Initialize the Backtester object and perform the backtest
    backtester = Backtester(stocks, start_date, end_date, "1d")
    portfolio_value, daily_returns = backtester.backtest(capital, is_buy, is_sell)

    # Calculate and print the Sharpe ratio
    sharpe_ratio = calculate_sharpe_ratio(daily_returns)
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

    # Print the final portfolio value
    print(portfolio_value)