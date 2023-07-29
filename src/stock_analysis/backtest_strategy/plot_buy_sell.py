import json
import os
import yfinance as yf
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly
import pandas as pd


def determine_row_col(timeframe):
    if timeframe == "0.25":
        row = 1
        col = 1
    elif timeframe == "0.5":
        row = 1
        col = 2
    elif timeframe == "0.75":
        row = 2
        col = 1
    elif timeframe == "1":
        row = 2
        col = 2
    elif timeframe == "3":
        row = 3
        col = 1
    elif timeframe == "5":
        row = 3
        col = 2
    return row, col


# Directory
dir = "./src/stock_analysis/backtest_strategy"
date_str = "20230720"
date_stock_data = "20230720"

# Dates
start_date = datetime(year=2008, month=5, day=1)
end_date = datetime.now()

# List of stocks
date_stocks_list = "20230416"
index_name = "LQ45"
stocks = pd.read_csv(
    f"./src/stock_analysis/static/{date_stocks_list}_stocks_list_{index_name}.csv",
    index_col=0,
).index.to_list()

# Create folder
if not os.path.exists(f"{dir}/images/buy_sell"):
    os.mkdir(f"{dir}/images/buy_sell")

if not os.path.exists(f"{dir}/images/buy_sell/{date_str}"):
    os.mkdir(f"{dir}/images/buy_sell/{date_str}")

for stock in stocks:
    if not os.path.exists(f"{dir}/images/buy_sell/{date_str}/{stock}"):
        os.mkdir(f"{dir}/images/buy_sell/{date_str}/{stock}")

    with open(
        f"./src/stock_analysis/backtest_strategy/data/{date_stock_data}/{stock}/backtest_data.json"
    ) as file:
        stock_data = json.load(file)

    pe = pd.read_csv(
        f"./src/stock_analysis/backtest_strategy/data/{date_stock_data}/{stock}/pe_ratio.json",
        index_col=0,
    )
    pbv = pd.read_csv(
        f"./src/stock_analysis/backtest_strategy/data/{date_stock_data}/{stock}/pbv_ratio.json",
        index_col=0,
    )
    ps = pd.read_csv(
        f"./src/stock_analysis/backtest_strategy/data/{date_stock_data}/{stock}/ps_ratio.json",
        index_col=0,
    )

    yf_stock = yf.Ticker(f"{stock}.JK")

    # Get price data from yfinance
    stock_price = (
        yf_stock.history(start=start_date, end=end_date, auto_adjust=False)
        .Close.reset_index()
        .set_index("Date")
    )

    for multiple, strat_types in stock_data.items():
        for strat_type, timeframes in strat_types.items():
            fig = make_subplots(
                rows=3,
                cols=2,
                subplot_titles=(
                    f"Backward timeframe: 0.25 year",
                    f"Backward timeframe: 0.5 year",
                    f"Backward timeframe: 0.75 year",
                    f"Backward timeframe: 1 year",
                    f"Backward timeframe: 3 year",
                    f"Backward timeframe: 5 year",
                ),
                specs=[
                    [{"secondary_y": True}, {"secondary_y": True}],
                    [{"secondary_y": True}, {"secondary_y": True}],
                    [{"secondary_y": True}, {"secondary_y": True}],
                ],
            )

            for timeframe, profit in timeframes.items():
                row, col = determine_row_col(timeframe)
                fig.add_trace(
                    go.Scatter(
                        x=stock_price.index,
                        y=stock_price.Close,
                        mode="lines",
                        name="Stock Price",
                        line=dict(
                            color=plotly.colors.qualitative.Plotly[2],
                        ),
                    ),
                    row=row,
                    col=col,
                )
                if multiple == "pe":
                    fig.add_trace(
                        go.Scatter(
                            x=pe.index,
                            y=pe["pe"],
                            mode="lines",
                            name="PE",
                            line=dict(
                                color=plotly.colors.qualitative.Plotly[3],
                            ),
                        ),
                        row=row,
                        col=col,
                        secondary_y=True,
                    )
                    fig.update_yaxes(
                        title_text="PE", row=row, col=col, secondary_y=True
                    )
                elif multiple == "pbv":
                    fig.add_trace(
                        go.Scatter(
                            x=pbv.index,
                            y=pbv["pbv"],
                            mode="lines",
                            name="PBV",
                            line=dict(
                                color=plotly.colors.qualitative.Plotly[4],
                            ),
                        ),
                        row=row,
                        col=col,
                        secondary_y=True,
                    )
                    fig.update_yaxes(
                        title_text="PBV", row=row, col=col, secondary_y=True
                    )
                elif multiple == "ps":
                    fig.add_trace(
                        go.Scatter(
                            x=ps.index,
                            y=ps["ps"],
                            mode="lines",
                            name="PS",
                            line=dict(
                                color=plotly.colors.qualitative.Plotly[4],
                            ),
                        ),
                        row=row,
                        col=col,
                        secondary_y=True,
                    )
                    fig.update_yaxes(
                        title_text="PS", row=row, col=col, secondary_y=True
                    )
                if len(profit) > 0:
                    timestamps_buy = [
                        transaction["timestamp_buy"]
                        for transaction in profit["profits"]
                    ]
                    # for timestamp_buy in timestamps_buy:
                    #     fig.add_vline(
                    #         x=timestamp_buy,
                    #         line_width=1,
                    #         name="Buy Price",
                    #         line_color=plotly.colors.qualitative.Plotly[0],
                    #         row=row,
                    #         col=col,
                    #     )

                    # first_timestamps_buy = [
                    #     timestamp["first_timestamp_buy"]
                    #     for timestamp in profit["profits"]
                    # ]
                    # for first_timestamp_buy in first_timestamps_buy:
                    #     fig.add_vline(
                    #         x=first_timestamp_buy,
                    #         line_width=1,
                    #         name="First Buy Price",
                    #         line_color=plotly.colors.qualitative.Plotly[5],
                    #         row=row,
                    #         col=col,
                    #     )
                    # timestamps_sell = [
                    #     timestamp["timestamp_sell"] for timestamp in profit["profits"]
                    # ]

                    prices_buy = [
                        [
                            stock_price.loc[timestamp]["Close"]
                            for timestamp in timestamp_buy
                        ]
                        for timestamp_buy in timestamps_buy
                    ]
                    for timestamp_buy, price_buy in zip(timestamps_buy, prices_buy):
                        fig.add_trace(
                            go.Scatter(
                                x=timestamp_buy,
                                y=price_buy,
                                mode="markers",
                                name="Buy Price",
                                marker=dict(
                                    size=6,
                                    color=plotly.colors.qualitative.Plotly[0],
                                ),
                            ),
                            row=row,
                            col=col,
                        )

                    # for timestamp_sell in timestamps_sell:
                    #     fig.add_vline(
                    #         x=timestamp_sell,
                    #         line_width=1,
                    #         name="Sell Price",
                    #         line_color=plotly.colors.qualitative.Plotly[1],
                    #         row=row,
                    #         col=col,
                    #     )

                    # last_timestamps_buy = [
                    #     timestamp["last_timestamp_buy"]
                    #     for timestamp in profit["profits"]
                    # ]
                    # for last_timestamp_buy in last_timestamps_buy:
                    #     fig.add_vline(
                    #         x=last_timestamp_buy,
                    #         line_width=1,
                    #         name="Last Buy Price",
                    #         line_color=plotly.colors.qualitative.Plotly[5],
                    #         row=row,
                    #         col=col,
                    #     )

                    timestamps_sell = [
                        transaction["timestamp_sell"]
                        for transaction in profit["profits"]
                    ]

                    prices_sell = [
                        stock_price.loc[timestamp_sell]["Close"]
                        for timestamp_sell in timestamps_sell
                    ]
                    for timestamp_sell, price_sell in zip(timestamps_sell, prices_sell):
                        fig.add_trace(
                            go.Scatter(
                                x=[timestamp_sell],
                                y=[price_sell],
                                mode="markers",
                                name="Sell Price",
                                marker=dict(
                                    size=6,
                                    color=plotly.colors.qualitative.Plotly[1],
                                ),
                            ),
                            row=row,
                            col=col,
                        )

                    fig.update_xaxes(
                        title_text="Time",
                        row=row,
                        col=col,
                    )
                    fig.update_yaxes(
                        title_text="Stock Price", row=row, col=col, secondary_y=False
                    )
                fig.update_traces(showlegend=False)
                fig.update_layout(
                    width=1920,
                    height=1080,
                    title_text=f"{stock}: {multiple.upper()} {strat_type}stdev Buy & Sell Backtest",
                )
            fig.write_image(
                f"{dir}/images/buy_sell/{date_str}/{stock}/buy_sell_{multiple.upper()}_{strat_type}.png"
            )
