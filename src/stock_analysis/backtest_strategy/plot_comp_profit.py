import json
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
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

data = pd.DataFrame()

for stock, multiples in idx_30.items():
    for multiple, timeframes in multiples.items():
        for timeframe, profit in timeframes.items():
            data.loc[
                f"{stock}",
                f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]",
            ] = profit["profit_pct_comp"]

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
        row, col = determine_row_col(timeframe)
        fig.add_trace(
            go.Scatter(
                x=data[
                    data[f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"]
                    > 0
                ].index,
                y=data[
                    data[f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"]
                    > 0
                ][f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"],
                mode="markers",
                marker=dict(size=8, color=plotly.colors.qualitative.Plotly[0]),
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatter(
                x=data[
                    data[f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"]
                    < 0
                ].index,
                y=data[
                    data[f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"]
                    < 0
                ][f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"],
                mode="markers",
                marker=dict(size=8, color=plotly.colors.qualitative.Plotly[1]),
            ),
            row=row,
            col=col,
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[
                    data[
                        f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"
                    ].mean()
                    for x in range(0, len(data))
                ],
                mode="lines+text",
                marker=dict(size=8, color=plotly.colors.qualitative.Plotly[4]),
                text=[
                    ""
                    if x < (len(data) - 1)
                    else str(
                        round(
                            data[
                                f"Total Compounded Profit ({multiple.upper()}) [{timeframe}Y]"
                            ].mean()
                        )
                    )
                    + "%"
                    for x in range(0, len(data))
                ],
                textposition="top center",
                textfont=dict(color=plotly.colors.qualitative.Plotly[4]),
            ),
            row=row,
            col=col,
        )
        fig.update_xaxes(
            title_text="Stock",
            row=row,
            col=col,
            categoryorder="array",
            categoryarray=data.index,
        )
        fig.update_yaxes(title_text="Compounded Profit [%]", row=row, col=col)
    fig.update_traces(showlegend=False)
    fig.update_layout(
        width=1920,
        height=1080,
        title_text=f"{multiple.upper()} Total Compounded Profit",
    )
    fig.write_image(f"{dir}/images/comp_profit_{multiple.upper()}.png")
