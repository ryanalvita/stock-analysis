import json
import pandas as pd
from scipy.stats import zscore

with open(
    "./src/stock_analysis/backtest_strategy/multiples_momentum/multiples_momentum_yearly.json",
    "r",
) as f:
    results = json.load(f)

stocks_per_year = {}
for year, data in results.items():
    stocks_per_year[year] = {}
    df = pd.DataFrame(data).T
    df = df.dropna()

    # calculate z-scores for each metric
    df["ey_zscore"] = zscore(df["earnings_yield"])
    df["pi_zscore"] = zscore(df["pi_6_months"])

    # assign weightage to each metric
    weight_ey = 0.5
    weight_pi = 0.5

    # calculate composite score
    df["composite_score"] = weight_ey * df["ey_zscore"] + weight_pi * df["pi_zscore"]

    # rank stocks based on composite score
    df_ranked = df.sort_values("composite_score", ascending=False)

    for stock, row in df_ranked.iterrows():
        if len(stocks_per_year[year]) < 10:
            stocks_per_year[year][stock] = {}
            stocks_per_year[year][stock]["stock_price"] = row["stock_price"]

transactions = {}
hold = []
for year, row in stocks_per_year.items():
    transactions[year] = {}
    for stock, data in row.items():
        if year == "2008":
            transactions[year][stock] = {
                "transaction_type": "buy",
                "stock_price": data["stock_price"],
            }
            hold.append(stock)
        else:
            if stock not in hold:
                transactions[year][stock] = {
                    "transaction_type": "buy",
                    "stock_price": data["stock_price"],
                }
                hold.append(stock)
            else:
                transactions[year][stock] = {
                    "transaction_type": "sell",
                    "stock_price": data["stock_price"],
                }
                hold.remove(stock)

test = 1
