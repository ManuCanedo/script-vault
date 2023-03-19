from scipy.optimize import minimize

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf


def fetch_stock_data(stock_list, start_date, end_date):
    stock_data = yf.download(stock_list, start=start_date, end=end_date)["Adj Close"]
    return stock_data


def calculate_daily_returns(stock_data):
    daily_returns = stock_data.pct_change().dropna()
    return daily_returns


def calculate_covariance_matrix(daily_returns):
    covariance_matrix = daily_returns.cov()
    return covariance_matrix


def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    portfolio_return = np.sum(mean_returns * weights) * 252
    portfolio_std_dev = np.sqrt(
        np.dot(weights.T, np.dot(cov_matrix, weights))
    ) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev
    return -sharpe_ratio


def optimal_allocation(mean_returns, cov_matrix, risk_free_rate=0.02):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)

    constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for asset in range(num_assets))
    result = minimize(
        neg_sharpe_ratio,
        num_assets * [1.0 / num_assets],
        args=args,
        bounds=bounds,
        constraints=constraints,
    )
    return result.x


def efficient_frontier(
    mean_returns, cov_matrix, num_portfolios=10000, risk_free_rate=0.02
):
    np.random.seed(42)
    num_assets = len(mean_returns)
    results = np.zeros((3 + num_assets, num_portfolios))

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        portfolio_return = np.sum(mean_returns * weights) * 252
        portfolio_std_dev = np.sqrt(
            np.dot(weights.T, np.dot(cov_matrix, weights))
        ) * np.sqrt(252)
        results[0, i] = portfolio_std_dev
        results[1, i] = portfolio_return
        results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
        results[3:, i] = weights

    return results


def main(stock_list, start_date, end_date):
    stock_data = fetch_stock_data(stock_list, start_date, end_date)
    daily_returns = calculate_daily_returns(stock_data)

    mean_returns = daily_returns.mean()[stock_list]
    cov_matrix = (
        daily_returns.cov().reindex(stock_list, axis=0).reindex(stock_list, axis=1)
    )

    optimal_weights = optimal_allocation(mean_returns, cov_matrix)

    portfolio_return = np.sum(mean_returns * optimal_weights) * 252
    portfolio_std_dev = np.sqrt(
        np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
    ) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - 0.02) / portfolio_std_dev

    frontier_data = efficient_frontier(mean_returns, cov_matrix)

    return (
        {stock: weight for stock, weight in zip(stock_list, optimal_weights)},
        frontier_data,
        (portfolio_std_dev, portfolio_return, sharpe_ratio),
    )


def plot_efficient_frontier(frontier_data, optimal_portfolio_metrics):
    plt.figure(figsize=(10, 6))
    plt.scatter(
        frontier_data[0, :], frontier_data[1, :], c=frontier_data[2, :], cmap="viridis"
    )
    plt.colorbar(label="Sharpe Ratio")
    plt.scatter(
        optimal_portfolio_metrics[0],
        optimal_portfolio_metrics[1],
        c="red",
        marker="*",
        s=200,
        label="Optimal Portfolio",
    )
    plt.xlabel("Volatility")
    plt.ylabel("Return")
    plt.title("Efficient Frontier")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    stock_list = ["TSLA", "VEVE.L", "SPY", "BRK-B", "MSFT"]
    start_date = "2013-01-01"
    end_date = "2022-12-31"

    optimal_weights, frontier_data, optimal_portfolio_metrics = main(
        stock_list, start_date, end_date
    )
    print("Optimal weights:")
    for stock, weight in optimal_weights.items():
        print(f"{stock}: {weight:.6f}")

    print("\nOptimal Portfolio Metrics:")
    print(f"Risk: {optimal_portfolio_metrics[0]:.6f}")
    print(f"Return: {optimal_portfolio_metrics[1]:.6f}")
    print(f"Sharpe Ratio: {optimal_portfolio_metrics[2]:.6f}")

    plot_efficient_frontier(frontier_data, optimal_portfolio_metrics)
