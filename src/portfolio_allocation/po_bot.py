import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

from scipy.optimize import minimize


def fetch_stock_data(stock_list, start_date, end_date):
    stock_data = yf.download(stock_list, start=start_date, end=end_date)["Adj Close"]
    return stock_data


def calculate_daily_returns(stock_data):
    daily_returns = stock_data.pct_change().dropna()
    return daily_returns


def calculate_covariance_matrix(daily_returns):
    covariance_matrix = daily_returns.cov()
    return covariance_matrix


def efficient_frontier(
    mean_returns, cov_matrix, num_portfolios=10000, risk_free_rate=0.02
):
    np.random.seed(42)
    num_assets = len(mean_returns)
    results = np.zeros((3, num_portfolios))

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

    return results


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


def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    portfolio_return = np.sum(mean_returns * weights) * 252
    portfolio_std_dev = np.sqrt(
        np.dot(weights.T, np.dot(cov_matrix, weights))
    ) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev
    return -sharpe_ratio


def main(stock_list, start_date, end_date):
    stock_data = fetch_stock_data(stock_list, start_date, end_date)
    daily_returns = calculate_daily_returns(stock_data)
    mean_returns = daily_returns.mean()
    cov_matrix = calculate_covariance_matrix(daily_returns)
    optimal_weights = optimal_allocation(mean_returns, cov_matrix)

    # Calculate risk, return, and Sharpe Ratio for the optimal portfolio
    portfolio_return = np.sum(mean_returns * optimal_weights) * 252
    portfolio_std_dev = np.sqrt(
        np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights))
    ) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - 0.02) / portfolio_std_dev

    # Get efficient frontier data
    frontier_data = efficient_frontier(mean_returns, cov_matrix)

    return (
        optimal_weights,
        frontier_data,
        (portfolio_std_dev, portfolio_return, sharpe_ratio),
    )


def display_frontier_table(stock_list, frontier_data, top_n=5):
    # Sort frontier_data based on Sharpe Ratio (in descending order)
    sorted_indices = np.argsort(frontier_data[2, :])[::-1]
    sorted_frontier_data = frontier_data[:, sorted_indices]

    # Select top_n portfolios
    top_frontier_data = sorted_frontier_data[:, :top_n]

    num_portfolios = top_frontier_data.shape[1]
    data = {
        "Risk": top_frontier_data[0, :],
        "Return": top_frontier_data[1, :],
        "Sharpe Ratio": top_frontier_data[2, :],
    }

    for i, stock in enumerate(stock_list):
        data[stock] = top_frontier_data[3 + i, :]

    df = pd.DataFrame(data).T
    df.columns = [f"Portfolio {i + 1}" for i in range(num_portfolios)]
    print(df)


def efficient_frontier(
    mean_returns, cov_matrix, num_portfolios=10, risk_free_rate=0.02
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


stock_list = ["VEVE.L", "BRK-B", "TSLA", "MSFT"]
start_date = "2016-01-01"
end_date = "2023-03-15"

optimal_weights, frontier_data, optimal_portfolio_metrics = main(
    stock_list, start_date, end_date
)
print("Optimal weights:")
print(optimal_weights)

# Print optimal portfolio metrics
print("\nOptimal Portfolio Metrics:")
print(f"Risk: {optimal_portfolio_metrics[0]:.6f}")
print(f"Return: {optimal_portfolio_metrics[1]:.6f}")
print(f"Sharpe Ratio: {optimal_portfolio_metrics[2]:.6f}")

# Display the frontier table
print("\nFrontier Portfolios:")
display_frontier_table(stock_list, frontier_data)

# Plot the efficient frontier
plt.figure(figsize=(10, 6))
plt.scatter(
    frontier_data[0, :], frontier_data[1, :], c=frontier_data[2, :], cmap="viridis"
)
plt.colorbar(label="Sharpe Ratio")
plt.xlabel("Volatility")
plt.ylabel("Return")
plt.title("Efficient Frontier")
plt.show()
