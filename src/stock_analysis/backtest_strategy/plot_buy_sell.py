import json
import os
import yfinance as yf
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly


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


dir = "./src/stock_analysis/backtest_strategy"

if not os.path.exists(f"{dir}/images"):
    os.mkdir(f"{dir}/images")

# Dates
start_date = datetime(year=2008, month=5, day=1)
end_date = datetime.now()

with open(f"{dir}/idx_30_backtest.json") as file:
    idx_30 = json.load(file)

for stock, multiples in idx_30.items():
    yf_stock = yf.Ticker(f"{stock}.JK")

    # Get price data from yfinance
    stock_price = (
        yf_stock.history(start=start_date, end=end_date, auto_adjust=False)
        .Close.reset_index()
        .set_index("Date")
    )
    stock_price.index = stock_price.tz_localize(None).index

    for multiple, timeframes in multiples.items():
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
        )

        for timeframe, profit in timeframes.items():
            timestamps_buy = [
                timestamp["timestamp_buy"] for timestamp in profit["data"]
            ]
            prices_buy = [timestamp["price_buy"] for timestamp in profit["data"]]
            timestamps_sell = [
                timestamp["timestamp_sell"] for timestamp in profit["data"]
            ]
            prices_sell = [timestamp["price_sell"] for timestamp in profit["data"]]

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
            # Add traces
            fig.add_trace(
                go.Scatter(
                    x=timestamps_buy,
                    y=prices_buy,
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
            # Add traces
            fig.add_trace(
                go.Scatter(
                    x=timestamps_sell,
                    y=prices_sell,
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
            fig.update_yaxes(title_text="Stock Price", row=row, col=col)
        fig.update_traces(showlegend=False)
        fig.update_layout(
            width=1920,
            height=1080,
            title_text=f"{stock}: {multiple.upper()} Buy & Sell Backtest",
        )
        fig.write_image(f"{dir}/images/buy_sell_{stock}_{multiple.upper()}.png")
