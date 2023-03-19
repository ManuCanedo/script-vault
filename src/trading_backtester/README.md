# Backtester for Trading Strategies

This project is a backtester for trading strategies built using Python. It enables you to test custom buy and sell strategies on historical stock data and evaluate the performance of the strategies. The backtester calculates the final portfolio value and the Sharpe Ratio, a measure of risk-adjusted returns, to help you evaluate the effectiveness of your trading strategies.

## Features

Fetches historical stock data from Yahoo Finance
Customizable buy and sell functions to test different trading strategies
Calculates the final portfolio value and the Sharpe Ratio
Supports rebalancing and portfolio allocation targets

## Usage

1. Modify the stocks, capital, start_date, and end_date variables in brv-bot.py to specify the stocks you want to backtest, the initial amount of capital, and the date range for the backtest.
2. Implement your own buy and sell functions (is_buy and is_sell in brv-bot.py). The functions should take a stock, stock data, and a portfolio as arguments and return a boolean value indicating whether to buy or sell the stock.
3. Run the backtester: `python brv-bot.py`
4. The backtester will print the Sharpe Ratio and the final portfolio value to the console.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
