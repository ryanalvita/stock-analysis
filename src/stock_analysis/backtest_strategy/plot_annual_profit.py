import json
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
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


# Directory
dir = "./src/stock_analysis/backtest_strategy"
date_str = "20230720"
date_stock_data = "20230720"

# Lists
multiples_list = ["pe", "pbv", "ps"]
strat_types_list = ["-1+1", "-1+2", "-2+1", "-2+2", "-2+0", "+0+2"]
timeframes_list = ["0.25", "0.5", "0.75", "1", "3", "5"]
index_name_list = ["IDX30", "LQ45", "IDX80", "KOMPAS100"]

# List of stocks
date_stocks_list = "20230416"
for index_name in index_name_list:
    stocks = pd.read_csv(
        f"./src/stock_analysis/static/{date_stocks_list}_stocks_list_{index_name}.csv",
        index_col=0,
    ).index.to_list()
    # Create folder
    if not os.path.exists(f"{dir}/images/annual_profit/"):
        os.mkdir(f"{dir}/images/annual_profit/")

    if not os.path.exists(f"{dir}/images/annual_profit/{date_str}"):
        os.mkdir(f"{dir}/images/annual_profit/{date_str}")

    if not os.path.exists(f"{dir}/images/annual_profit/{date_str}/{index_name}"):
        os.mkdir(f"{dir}/images/annual_profit/{date_str}/{index_name}")

    results = {}
    for stock in stocks:
        with open(
            f"./src/stock_analysis/backtest_strategy/data/{date_stock_data}/{stock}/backtest_data.json"
        ) as file:
            data = json.load(file)
        results.update({stock: data})

    df = pd.DataFrame()
    for stock, multiples in results.items():
        for multiple, strat_types in multiples.items():
            for strat_type, timeframes in strat_types.items():
                for timeframe, profit in timeframes.items():
                    if len(profit) > 0:
                        df.loc[
                            f"{stock}",
                            f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]",
                        ] = profit["annual_profit"]
                    else:
                        df.loc[
                            f"{stock}",
                            f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]",
                        ] = 0

    for multiple in multiples_list:
        for strat_type in strat_types_list:
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
            for timeframe in timeframes_list:
                row, col = determine_row_col(timeframe)
                fig.add_trace(
                    go.Scatter(
                        x=df[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ]
                            > 0
                        ].index,
                        y=df[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ]
                            > 0
                        ][
                            f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                        ],
                        mode="markers",
                        marker=dict(size=8, color=plotly.colors.qualitative.Plotly[0]),
                    ),
                    row=row,
                    col=col,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ]
                            < 0
                        ].index,
                        y=df[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ]
                            < 0
                        ][
                            f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                        ],
                        mode="markers",
                        marker=dict(size=8, color=plotly.colors.qualitative.Plotly[1]),
                    ),
                    row=row,
                    col=col,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ].mean()
                            for x in range(0, len(df))
                        ],
                        mode="lines+text",
                        marker=dict(size=8, color=plotly.colors.qualitative.Plotly[4]),
                        text=[
                            ""
                            if x < (len(df) - 1)
                            else str(
                                round(
                                    df[
                                        f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                                    ].mean()
                                )
                            )
                            + "%"
                            for x in range(0, len(df))
                        ],
                        textposition="top center",
                        textfont=dict(color=plotly.colors.qualitative.Plotly[4]),
                    ),
                    row=row,
                    col=col,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ].mean()
                            + df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ].std()
                            for x in range(0, len(df))
                        ],
                        mode="lines+text",
                        marker=dict(size=8, color=plotly.colors.qualitative.Plotly[6]),
                        text=[
                            ""
                            if x < (len(df) - 1)
                            else str(
                                round(
                                    df[
                                        f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                                    ].mean()
                                    + df[
                                        f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                                    ].std()
                                )
                            )
                            + "%"
                            for x in range(0, len(df))
                        ],
                        textposition="top center",
                        textfont=dict(color=plotly.colors.qualitative.Plotly[6]),
                    ),
                    row=row,
                    col=col,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=[
                            df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ].mean()
                            - df[
                                f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                            ].std()
                            for x in range(0, len(df))
                        ],
                        mode="lines+text",
                        marker=dict(size=8, color=plotly.colors.qualitative.Plotly[6]),
                        text=[
                            ""
                            if x < (len(df) - 1)
                            else str(
                                round(
                                    df[
                                        f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                                    ].mean()
                                    - df[
                                        f"Annual Profit ({multiple.upper()}) [{timeframe}Y, {strat_type}]"
                                    ].std()
                                )
                            )
                            + "%"
                            for x in range(0, len(df))
                        ],
                        textposition="top center",
                        textfont=dict(color=plotly.colors.qualitative.Plotly[6]),
                    ),
                    row=row,
                    col=col,
                )
                fig.update_xaxes(
                    title_text="Stock",
                    row=row,
                    col=col,
                    categoryorder="array",
                    categoryarray=df.index,
                )
                fig.update_yaxes(title_text="Annual Profit [%]", row=row, col=col)
            fig.update_traces(showlegend=False)
            fig.update_layout(
                width=1920,
                height=1080,
                title_text=f"{multiple.upper()} {strat_type}stdev Annual Profit Percentage - {index_name}",
            )
            fig.write_image(
                f"{dir}/images/annual_profit/{date_str}/{index_name}/{multiple.upper()}_{strat_type}.png"
            )
