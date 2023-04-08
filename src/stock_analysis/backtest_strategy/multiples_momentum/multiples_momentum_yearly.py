import json
import os
import yfinance as yf
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly
import pandas as pd
from pymongo import MongoClient
from stock_analysis.utils import clean_dataframe
import numpy as np

# Define a function to get the quarter deadline for a given quarter and year


# Dates


years = [year for year in range(2008, 2023)]

stocks_csv = pd.read_csv(
    "./src/stock_analysis/static/20230402_stocks_list_LQ45.csv", index_col=0
)
stocks_list = [row.to_list() for _, row in stocks_csv.iterrows()]
stocks_list = set([stock for stock_list in stocks_list for stock in stock_list])

# Collect stock data
data = {}
cluster = MongoClient(os.environ["MONGODB_URI"])
db = cluster["stockbit_data"]
collection = db["yearly"]
for stock in stocks_list:
    stock_data = collection.find_one({"stock_code": stock})
    data[stock] = stock_data

results = {}

for year in years:
    results.update({f"{str(year)}": {}})
    start_date = datetime(year=year, month=5, day=1)
    end_date = datetime(year=year, month=6, day=1)

    stocks = stocks_csv[str(year)].to_list()

    for stock in stocks:
        results[str(year)].update({f"{stock}": {}})

        yf_stock = yf.Ticker(f"{stock}.JK")
        try:
            stock_price = yf_stock.history(
                start=start_date, end=end_date, auto_adjust=False
            ).iloc[0]["Close"]
            stock_price_6months = yf_stock.history(
                start=start_date - pd.DateOffset(months=6),
                end=end_date - pd.DateOffset(months=6),
                auto_adjust=False,
            ).iloc[0]["Close"]
            earnings_yield = (
                float(data[stock]["income_statement"][str(year)]["EPS (Annual)"])
                / stock_price
            ) * 100
            book_value_yield = (
                float(
                    data[stock]["balance_sheet"][str(year)][
                        "Book Value Per Share (Annual)"
                    ]
                )
                / stock_price
            ) * 100
            pi_6_months = stock_price / stock_price_6months
        except:
            stock_price = np.nan
            stock_price_6months = np.nan
            earnings_yield = np.nan
            book_value_yield = np.nan
            pi_6_months = np.nan

        results[str(year)][stock].update(
            {
                "stock_price": stock_price,
                "stock_price_6months": stock_price_6months,
                "earnings_yield": earnings_yield,
                "book_value_yield": book_value_yield,
                "pi_6_months": pi_6_months,
            }
        )

# Save the data in json
with open(
    f"src/stock_analysis/backtest_strategy/multiples_momentum/multiples_momentum_yearly.json",
    "w",
) as f:
    f.write(json.dumps(results, ensure_ascii=False))

test = 1

# fig = make_subplots(specs=[[{"secondary_y": True}]])

# # Get stock price data
# yf_stock = yf.Ticker(f"{stock}.JK")
# stock_price = (
#     yf_stock.history(start=start_date, end=end_date, auto_adjust=False)
#     .Close.reset_index()
#     .set_index("Date")
# )
# stock_price.index = stock_price.tz_localize(None).index
# spikes = stock_price["Close"].quantile(0.9999)
# stock_price = stock_price[stock_price["Close"] <= spikes]
# stock_price = stock_price.resample("D").interpolate(method="linear")

# # Get net income data
# cluster = MongoClient(os.environ["MONGODB_URI"])
# db = cluster["stockbit_data"]
# collection = db["quarterly"]
# data = collection.find_one({"stock_code": stock})
# df = clean_dataframe(pd.DataFrame(data["income_statement"]))

# # Reverse columns
# df = df.loc[:, ::-1]

# # extract the year from column names and create a year column
# df = df.rolling(4).sum()

# # Shift the data by 4 periods (one year)
# df_shifted = df.shift(4, axis=1)
# growth = (df - df_shifted) / df_shifted * 100
# df.loc["QoQ TTM Net Income Growth"] = growth.loc["Total Net Income Attributable To"]

# # Get release dates data
# cluster = MongoClient(os.environ["MONGODB_PERSONAL_URI"])
# db = cluster["stockbit_data"]
# collection = db["release_dates"]
# release_date = collection.find_one({"stock_code": stock})

# df_release_date = pd.DataFrame(release_date["release_dates"])
# data = pd.DataFrame()

# for keyword in ["Laporan Keuangan Tahunan", "Laporan Keuangan Interim"]:
#     _data = df_release_date[
#         df_release_date["title"].str.contains(keyword, case=False)
#     ].reset_index(drop=True)

#     # Convert the 'date' column to a pandas datetime object
#     _data["date"] = pd.to_datetime(_data["date"])

#     if "Tahunan" in keyword:
#         # Apply the 'get_quarter_deadline' function to the 'quarter' and 'year' columns to get the quarter deadlines
#         _data["quarter_deadline"] = _data.apply(
#             lambda row: get_quarter_deadline_tahunan(row["date"]), axis=1
#         )

#     elif "Interim" in keyword:
#         _data["quarter_deadline"] = _data.apply(
#             lambda row: get_quarter_deadline_interim(row["date"]), axis=1
#         )

#     data = pd.concat([data, _data], axis=0)

# # Group the data by quarter and year, and get the earliest release date for each group
# quarterly_data = (
#     data.groupby(["quarter_deadline"])
#     .agg({"date": "min"})
#     .reset_index()
#     .sort_values("date")
# )
# (
#     quarterly_data["quarter"],
#     quarterly_data["year"],
# ) = zip(*quarterly_data["quarter_deadline"].apply(get_quarter_year))
# quarterly_data.index = quarterly_data.apply(
#     lambda row: f"Q{row['quarter']} {row['year']}", axis=1
# )
# quarterly_data = quarterly_data.drop(
#     ["year", "quarter", "quarter_deadline"], axis=1
# )
# quarterly_data = quarterly_data.rename(columns={"date": "Release Date"})

# df = pd.concat([df, quarterly_data.T])

# # Figure
# # Cut stock price
# stock_price = stock_price[stock_price.index >= min(df.loc["Release Date"].dropna())]

# fig.add_trace(
#     go.Scatter(
#         x=stock_price.index,
#         y=stock_price.Close,
#         mode="lines",
#         name="Stock Price",
#         line=dict(
#             color=plotly.colors.qualitative.Plotly[0],
#             width=2,
#         ),
#     ),
# )

# # Marker on price
# fig.add_trace(
#     go.Scatter(
#         x=stock_price.loc[df.loc["Release Date"].dropna().values].index,
#         y=stock_price.loc[df.loc["Release Date"].dropna()]["Close"].values,
#         mode="markers",
#         name="Stock Price",
#         marker=dict(
#             size=12,
#             color=plotly.colors.qualitative.Plotly[1],
#         ),
#     ),
# )

# fig.add_trace(
#     go.Scatter(
#         x=df.loc["Release Date"],
#         y=df.loc["QoQ TTM Net Income Growth"],
#         mode="lines+markers",
#         name="QoQ TTM Net Income Growth",
#         marker=dict(
#             size=12,
#         ),
#         line=dict(
#             width=2,
#             color=plotly.colors.qualitative.Plotly[2],
#         ),
#         yaxis="y2",
#     ),
# )

# fig.add_trace(
#     go.Scatter(
#         x=df.loc["Release Date"],
#         y=df.loc["Total Net Income Attributable To"],
#         mode="lines+markers",
#         name="Net Income",
#         marker=dict(
#             size=12,
#         ),
#         line=dict(
#             width=2,
#             color=plotly.colors.qualitative.Plotly[3],
#         ),
#         yaxis="y3",
#     ),
# )

# # Plot finishup
# fig.update_traces(showlegend=False)
# fig.update_layout(
#     width=1920,
#     height=1080,
#     title_text=f"{stock}",
# )

# fig.update_layout(
#     yaxis=dict(
#         title="Stock Price",
#     ),
#     yaxis2=dict(
#         title="Release Date",
#         overlaying="y",
#         side="right",
#     ),
#     yaxis3=dict(
#         title="Net Income", anchor="y", overlaying="y", side="right", position=1
#     ),
#     # yaxis4=dict(
#     #     title="PE Ratio",
#     #     anchor="y",
#     #     overlaying="y",
#     #     side="right",
#     #     position=1
#     # ),
# )

# # fig.update_layout(yaxis2=dict(type='log')) # update
# fig.show()
# # fig.write_image(f"{dir}/images/buy_sell_{stock}_{multiple.upper()}.png")
