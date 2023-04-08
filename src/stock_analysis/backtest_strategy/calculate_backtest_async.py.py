import asyncio, time
import numpy as np
import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from pymongo import MongoClient

start_run = time.time()


def determine_quarter_col(date):
    year = date.year
    if (
        datetime(day=1, month=11, year=year - 1)
        <= date
        <= datetime(day=31, month=3, year=year)
    ):
        col = f"Q3 {str(year - 1)}"
    elif (
        datetime(day=1, month=4, year=year)
        <= date
        <= datetime(day=30, month=4, year=year)
    ):
        col = f"Q4 {str(year - 1)}"
    elif (
        datetime(day=1, month=5, year=year)
        <= date
        <= datetime(day=31, month=7, year=year)
    ):
        col = f"Q1 {str(year)}"
    elif (
        datetime(day=1, month=8, year=year)
        <= date
        <= datetime(day=31, month=10, year=year)
    ):
        col = f"Q2 {str(year)}"
    elif (
        datetime(day=1, month=11, year=year)
        <= date
        <= datetime(day=31, month=3, year=year + 1)
    ):
        col = f"Q3 {str(year)}"
    elif (
        datetime(day=1, month=4, year=year + 1)
        <= date
        <= datetime(day=30, month=4, year=year + 1)
    ):
        col = f"Q4 {str(year)}"

    return col


def calculate_final_percentage(initial_value, profit_loss_percentages):
    percentage_changes = np.array(profit_loss_percentages) / 100.0
    final_value = initial_value * np.prod(1 + percentage_changes)
    percentage_change = ((final_value - initial_value) / initial_value) * 100
    return percentage_change


def determine_col_previous(col):
    period = int(col[1:2])
    year = int(col[-4:])
    if "Q1" in col:
        col_previous = f"Q4 {year-1}"
    else:
        col_previous = f"Q{period-1} {year}"
    return col_previous


# MongoDB
cluster = MongoClient(
    "mongodb+srv://mongo:KgWIfb4AzqkTyDXb@stockanalysis.f30kw8z.mongodb.net/?retryWrites=true&w=majority"
)

# Get data
db_stockbit_data = cluster["stockbit_data"]
collection_quarterly = db_stockbit_data["quarterly"]
collection_ttm = db_stockbit_data["ttm"]

# Dates
start_date = datetime(year=2008, month=5, day=1)
end_date = datetime.now()

# Get IDX 30 stocks list
stocks = pd.read_csv(
    "./src/stock_analysis/static/20230402_stocks_list.csv", index_col=0
).index.to_list()[0:3]

idx_30 = {}
timeframes = [0.25, 0.5, 0.75, 1, 3, 5]


async def loop_multiple(multiple, results, pe, pbv, stock_price):
    for multiple in ["pe", "pbv"]:
        if multiple == "pe":
            df = pe
        elif multiple == "pbv":
            df = pbv

        results[f"{multiple}"] = {}

        for tf in timeframes:
            days = round(365 * tf)
            df[f"mean_{tf}y"] = df[f"{multiple}"].rolling(f"{str(days)}d").mean()
            df[f"stdev_{tf}y"] = df[f"{multiple}"].rolling(f"{str(days)}d").std()
            df[f"mean_+1_stdev_{tf}y"] = df[f"mean_{tf}y"] + df[f"stdev_{tf}y"]
            df[f"mean_-1_stdev_{tf}y"] = df[f"mean_{tf}y"] - df[f"stdev_{tf}y"]

            # Determine timestamp buy/sell
            bought = False
            timestamp_buy = []
            timestamp_sell = []

            for ix, row in df.iterrows():
                if row[f"{multiple}"] < row[f"mean_-1_stdev_{tf}y"] and bought == False:
                    # col = determine_quarter_col(start_date, ix)
                    # year = ix.year
                    # col_previous = determine_col_previous(col)
                    # if (
                    #     df_is.loc["Net Income Attributable To", col]
                    #     > df_is.loc["Net Income Attributable To", col_previous]
                    # ):
                    bought = True
                    timestamp_buy.append(ix)
                elif (
                    row[f"{multiple}"] > row[f"mean_+1_stdev_{tf}y"] and bought == True
                ):
                    bought = False
                    timestamp_sell.append(ix)

            profits = []

            for (buy, sell) in zip(timestamp_buy, timestamp_sell):
                profit = {}
                profit["timestamp_buy"] = str(buy)
                profit["timestamp_sell"] = str(sell)
                profit["price_buy"] = stock_price.loc[buy].values[0]
                profit["price_sell"] = stock_price.loc[sell].values[0]
                profit["profit_pct"] = (
                    (profit["price_sell"] - profit["price_buy"])
                    / profit["price_buy"]
                    * 100
                )
                profit["profit_pct_per_year"] = profit["profit_pct"] / (
                    (sell - buy).days / 365
                )

                profit[f"{multiple}_buy"] = df.loc[buy, f"{multiple}"]
                profit[f"{multiple}_mean_{tf}y_buy"] = df.loc[buy, f"mean_{tf}y"]
                profit[f"{multiple}_mean_+1_stdev_{tf}y_buy"] = df.loc[
                    buy, f"mean_+1_stdev_{tf}y"
                ]
                profit[f"{multiple}_mean_-1_stdev_{tf}y_buy"] = df.loc[
                    buy, f"mean_-1_stdev_{tf}y"
                ]

                profit[f"{multiple}_sell"] = df.loc[sell, f"{multiple}"]
                profit[f"{multiple}_mean_{tf}y_sell"] = df.loc[sell, f"mean_{tf}y"]
                profit[f"{multiple}_mean_+1_stdev_{tf}y_sell"] = df.loc[
                    sell, f"mean_+1_stdev_{tf}y"
                ]
                profit[f"{multiple}_mean_-1_stdev_{tf}y_sell"] = df.loc[
                    sell, f"mean_-1_stdev_{tf}y"
                ]

                profits.append(profit)

            if len(profits) > 0:
                results[f"{multiple}"].update(
                    {
                        f"{tf}": {
                            "profit_pct_sum": sum(
                                profit["profit_pct"] for profit in profits
                            ),
                            "profit_pct_comp": calculate_final_percentage(
                                1, [profit["profit_pct"] for profit in profits]
                            ),
                            "average_profit_pct_per_year": sum(
                                profit["profit_pct_per_year"] for profit in profits
                            )
                            / len(profits),
                            "data": profits,
                        },
                    },
                )
            else:
                results[f"{multiple}"].update(
                    {
                        f"{tf}": {
                            "profit_pct_sum": 0,
                            "profit_pct_comp": 0,
                            "average_profit_pct_per_year": 0,
                            "data": profits,
                        },
                    },
                )


async def calculate_profit(stock, start_date, end_date, timeframes):
    data_quarterly = collection_quarterly.find_one({"stock_code": stock})
    data_ttm = collection_ttm.find_one({"stock_code": stock})
    yf_stock = yf.Ticker(f"{stock}.JK")

    df_is = pd.DataFrame(data_ttm["income_statement"])
    df_bs = pd.DataFrame(data_quarterly["balance_sheet"])

    # Stock yf
    splits = yf_stock.splits

    # Get price data from yfinance
    stock_price = (
        yf_stock.history(start=start_date, end=end_date, auto_adjust=False)
        .Close.reset_index()
        .set_index("Date")
    )
    stock_price.index = stock_price.tz_localize(None).index

    pe = pd.DataFrame()
    pbv = pd.DataFrame()

    for ix, values in stock_price.iterrows():
        try:
            col = determine_quarter_col(start_date, ix)

            pe.loc[ix, "pe"] = values.Close / (
                float(df_is.loc["Net Income Attributable To", col])
                / (float(df_is.loc["Share Outstanding", col]))
            )
            pbv.loc[ix, "pbv"] = values.Close / (
                float(df_bs.loc["Total Equity", col])
                / (float(df_is.loc["Share Outstanding", col]))
            )

        except:
            pe.loc[ix, "pe"] = np.nan
            pbv.loc[ix, "pbv"] = np.nan

    results = {}
    tasks_multiple = []
    for multiple in ["pe", "pbv"]:
        tasks_multiple.append(
            asyncio.create_task(loop_multiple(multiple, results, pe, pbv, stock_price))
        )
    await asyncio.gather(*tasks_multiple)

    idx_30.update({stock: results})


async def main():
    tasks = []
    for stock in stocks:
        tasks.append(
            asyncio.create_task(
                calculate_profit(stock, start_date, end_date, timeframes)
            )
        )
    await asyncio.gather(*tasks)


asyncio.run(main())
elapsed_time = time.time() - start_run
print(f"Elapsed time: {elapsed_time} seconds")


# with open("idx_30_backtest.json", "w") as outfile:
#     json.dump(idx_30, outfile)

test = 1
