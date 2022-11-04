import os
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
import plotly.graph_objs as go
import numpy as np

import seaborn as sns
import plotly.express as px
import plotly.io as pio
import yfinance as yf

# Functions
def clean_dataframe(df):
    try:
        df = df.drop(columns=["TTM"])
    except Exception:
        pass

    try:
        df = df.drop(columns=["Current"])
    except Exception:
        pass

    for index in df.index:
        try:
            df.loc[index] = df.loc[index].replace('', np.nan).replace('-', np.nan).replace('—', np.nan)
            df.loc[index] = df.loc[index].apply(lambda x: float(x))
        except Exception:
            df.loc[index] = np.nan

    for i in range(0, len(df.columns) - 5):
        df = df.drop(df.columns[range(0, len(df.columns) - 5)], axis=1)
    
    return df

def update_layout(fig, figtype):
    if figtype.lower() == "percentage":
        fig.update_layout(
            yaxis=dict(
                title='%',
                title_standoff=0
            )
        )
    elif figtype == "ratio":
        fig.update_layout(
            yaxis=dict(
                title='',
                title_standoff=0
            ),
        )
    elif figtype == "basic":
        fig.update_layout(
            yaxis=dict(
                title='IDR',
                title_standoff=0
            ),
            barmode='group',
            bargap=0.4, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1, # gap between bars of the same location coordinate.
        )
    fig.update_layout(    
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(
            family="Helvetica",
            size=12,
        ),
        width=500,
        height=250,
        margin=dict(
            l=25,
            r=25,
            b=25,
            t=25,
            pad=4
        ),
        template='ggplot2'
    )

    return fig

# Initialize MongoDB
cluster = MongoClient(os.environ["MONGODB_URI"])
db = cluster["financial_data"]

# Input
# Determine period_type
period_types = ["yearly", "quarterly"]

# Determine stock
stock = "BUMI"

# Determine color scheme
colors = ["#448AFF", "#FF9800", "#26C6DA", "#B388FF", "#3D4750"]

# Define date
datenow_str = datetime.strftime(datetime.now(), "%Y%m%d")

# Create folder if it is not exist
directory = f"images/{stock}/{datenow_str}"
if not os.path.exists(directory):
    os.makedirs(directory)

for period_type in period_types:
    collection = db[period_type]
    data = collection.find_one({"stock_code": stock})

    df_is = clean_dataframe(pd.DataFrame(data["income_statement"]))
    df_bs = clean_dataframe(pd.DataFrame(data["balance_sheet"]))
    df_cf = clean_dataframe(pd.DataFrame(data["cash_flow"]))
    df_rs = clean_dataframe(pd.DataFrame(data["ratios"]))

    # Fill df_rs
    df_rs.loc["Gross margin %"] = (df_is.loc["Gross profit"] / df_is.loc["Total revenue"]).values * 100
    df_rs.loc["Operating margin %"] = (df_is.loc["Operating income"] / df_is.loc["Total revenue"]).values * 100
    df_rs.loc["Net margin %"] = (df_is.loc["Net income"] / df_is.loc["Total revenue"]).values * 100

    df_rs.loc["Return on equity %"] = (df_is.loc["Net income"] / df_bs.loc["Total equity"]).values * 100
    df_rs.loc["Return on assets %"] = (df_is.loc["Net income"] / df_bs.loc["Total assets"]).values * 100

    df_rs.loc["Debt to equity ratio"] = (df_bs.loc["Total debt"] / df_bs.loc["Total equity"]).values
    df_rs.loc["Debt to assets ratio"] = (df_bs.loc["Total debt"] / df_bs.loc["Total assets"]).values

    # 01 - Revenue & Net Income
    fig1 = go.Figure(
        data=[
            go.Bar(name='Revenue', x=df_is.columns, y=df_is.loc["Total revenue"], marker_color=colors[0]),
            go.Bar(name='Net Income', x=df_is.columns, y=df_is.loc["Net income"], marker_color=colors[1]),
        ],
    )
    fig1 = update_layout(fig1, "basic")
    fig1.write_image(f"{directory}/01 Revenue & Net Income - {period_type}.png")
    
    # # 02 - Revenue & Net Income Growth
    # revenue_growth = df_is.loc["Total revenue"].pct_change()*100
    # net_income_growth = df_is.loc["Net income"].pct_change()*100
    # fig1a = go.Figure(
    #     data=[
    #         go.Scatter(x=revenue_growth.index, y=revenue_growth.values, name='Revenue Growth', mode='lines+markers', marker_color=colors[0], marker_line_color=colors[0]),
    #         go.Scatter(x=net_income_growth.index, y=net_income_growth.values, name='Net Income Growth', mode='lines+markers', marker_color=colors[1], marker_line_color=colors[1]),
    #     ]
    # )
    # fig1a = update_layout(fig1a, "growth")
    # fig1a.write_image(f"{directory}/01a Revenue & Net Income Growth - {period_type}.png")

    # 02 - Assets, Liabilites, and Equity
    fig2 = go.Figure(
        data=[
            go.Bar(name='Assets', x=df_bs.columns, y=df_bs.loc["Total assets"], marker_color=colors[0]),
            go.Bar(name='Liabilities', x=df_bs.columns, y=df_bs.loc["Total liabilities"], marker_color=colors[1]),
            go.Bar(name='Equity', x=df_bs.columns, y=df_bs.loc["Total equity"], marker_color=colors[2]),
        ],
    )
    fig2 = update_layout(fig2, "basic")
    fig2.write_image(f"{directory}/03 - Assets, Liabilites, and Equity - {period_type}.png")

    # # 02a - Assets, Liabilites, and Equity Growth
    # asset_growth = df_bs.loc["Total assets"].pct_change()*100
    # liabilities_growth = df_bs.loc["Total liabilities"].pct_change()*100
    # equity_growth = df_bs.loc["Total equity"].pct_change()*100
    # fig2a = go.Figure(
    #     data=[
    #         go.Scatter(x=asset_growth.index, y=asset_growth.values, name='Assets', mode='lines+markers', marker_color=colors[0], marker_line_color=colors[0]),
    #         go.Scatter(x=liabilities_growth.index, y=liabilities_growth.values, name='Liabilities', mode='lines+markers', marker_color=colors[1], marker_line_color=colors[1]),
    #         go.Scatter(x=equity_growth.index, y=equity_growth.values, name='Equity', mode='lines+markers', marker_color=colors[2], marker_line_color=colors[2]),
    #     ]
    # )
    # fig2a = update_layout(fig2a, "growth")
    # fig2a.write_image(f"{directory}/02a - Assets, Liabilites, and Equity Growth - {period_type}.png")

    # 03 - Cash flow from operating, investing, and financing activities
    fig3 = go.Figure(
        data=[
            go.Bar(name='Operating', x=df_cf.columns, y=df_cf.loc["Cash from operating activities"], marker_color=colors[0]),
            go.Bar(name='Investing', x=df_cf.columns, y=df_cf.loc["Cash from investing activities"], marker_color=colors[1]),
            go.Bar(name='Financing', x=df_cf.columns, y=df_cf.loc["Cash from financing activities"], marker_color=colors[2]),
        ],
    )
    fig3 = update_layout(fig3, "basic")
    fig3.write_image(f"{directory}/03 - Cash Flow from Operating, Investing, and Financing Activities - {period_type}.png")

    # # 03a - Cash flow from operating, investing, and financing activities growth
    # cash_flow_operating_growth = df_cf.loc["Cash from operating activities"].pct_change()*100
    # cash_flow_investing_growth = df_cf.loc["Cash from investing activities"].pct_change()*100
    # cash_flow_financing_growth = df_cf.loc["Cash from financing activities"].pct_change()*100
    # fig3a = go.Figure(
    #     data=[
    #         go.Scatter(x=cash_flow_operating_growth.index, y=cash_flow_operating_growth.values, name='Operating', mode='lines+markers', marker_color=colors[0], marker_line_color=colors[0]),
    #         go.Scatter(x=cash_flow_investing_growth.index, y=cash_flow_investing_growth.values, name='Investing', mode='lines+markers', marker_color=colors[1], marker_line_color=colors[1]),
    #         go.Scatter(x=cash_flow_financing_growth.index, y=cash_flow_financing_growth.values, name='Financing', mode='lines+markers', marker_color=colors[2], marker_line_color=colors[2]),
    #     ]
    # )
    # fig3a = update_layout(fig3a, "growth")
    # fig3a.write_image(f"{directory}/03a - Cash Flow from Operating, Investing, and Financing activities Growth - {period_type}.png")

    # 04 Profitability
    # 04a Profit Margin
    fig4a = go.Figure(
        data=[
            go.Scatter(name='Gross Margin', x=df_rs.columns, y=df_rs.loc["Gross margin %"], marker_color=colors[0], marker_line_color=colors[0]),
            go.Scatter(name='Operating Margin', x=df_rs.columns, y=df_rs.loc["Operating margin %"], marker_color=colors[1], marker_line_color=colors[1]),
            go.Scatter(name='Net margin', x=df_rs.columns, y=df_rs.loc["Net margin %"], marker_color=colors[2], marker_line_color=colors[2]),
        ],
    )
    fig4a = update_layout(fig4a, "percentage")
    fig4a.write_image(f"{directory}/04a Profitability (Margin) - {period_type}.png")

    # 04b Return
    fig4b = go.Figure(
        data=[
            go.Scatter(name='ROE', x=df_rs.columns, y=df_rs.loc["Return on equity %"], marker_color=colors[0], marker_line_color=colors[0]),
            go.Scatter(name='ROA', x=df_rs.columns, y=df_rs.loc["Return on assets %"], marker_color=colors[1], marker_line_color=colors[1]),
            go.Scatter(name='ROIC', x=df_rs.columns, y=df_rs.loc["Return on invested capital %"], marker_color=colors[2], marker_line_color=colors[2]),
        ],
    )
    fig4b = update_layout(fig4b, "percentage")
    fig4b.write_image(f"{directory}/04b Profitability (Return) - {period_type}.png")

    # 05 Solvability
    # 05a Solvency Ratio
    fig5a = go.Figure(
        data=[
            go.Scatter(name='Quick Ratio', x=df_rs.columns, y=df_rs.loc["Quick ratio"], marker_color=colors[0], marker_line_color=colors[0]),
            go.Scatter(name='Current Ratio', x=df_rs.columns, y=df_rs.loc["Current ratio"], marker_color=colors[1], marker_line_color=colors[1]),
        ],
    )
    fig5a = update_layout(fig5a, "ratio")
    fig5a.write_image(f"{directory}/05a Solvability (Solvency Ratio) - {period_type}.png")

    # 05b Debt Ratio
    fig5b = go.Figure(
        data=[
            go.Scatter(name='Debt to Equity Ratio', x=df_rs.columns, y=df_rs.loc["Debt to equity ratio"], marker_color=colors[0], marker_line_color=colors[0]),
            go.Scatter(name='Debt to Assets Ratio', x=df_rs.columns, y=df_rs.loc["Debt to assets ratio"], marker_color=colors[1], marker_line_color=colors[1]),
        ],
    )
    fig5b = update_layout(fig5b, "ratio")
    fig5b.write_image(f"{directory}/05b Solvability (Debt Ratio) - {period_type}.png")

    # 6 Valuation
    # Get stock price data
    if period_type == "yearly":
        stock_price = yf.Ticker(f"{stock}.JK").history(period='10y').Close
        for column, value in df_rs.iteritems():
            price = stock_price[stock_price.index.year == int(column)].mean()
            shares_outstanding = df_rs.loc["Total common shares outstanding", column]
            
            earnings_per_share = df_is.loc["Net income", column] / shares_outstanding
            df_rs.loc["Price to earnings ratio", column] = price / earnings_per_share

            book_value_per_share = df_bs.loc["Total equity", column] / shares_outstanding
            df_rs.loc["Price to book ratio", column] = price / book_value_per_share

        # 6a PE Valuation
        fig6a = go.Figure(
            data=[
                go.Scatter(name='PE Ratio', x=df_rs.columns, y=df_rs.loc["Price to earnings ratio"], marker_color=colors[0], marker_line_color=colors[0]),
            ],
        )
        fig6a = update_layout(fig6a, "ratio")
        fig6a.write_image(f"{directory}/06a Valuation (PE) - {period_type}.png")

        # 6a PE Valuation
        fig6b = go.Figure(
            data=[
                go.Scatter(name='PBV Ratio', x=df_rs.columns, y=df_rs.loc["Price to book ratio"], marker_color=colors[1], marker_line_color=colors[1]),
            ],
        )
        fig6b = update_layout(fig6b, "ratio")
        fig6b.write_image(f"{directory}/06b Valuation (PBV) - {period_type}.png")

        # 7 Shares outstanding
        fig7 = go.Figure(
            data=[
                go.Scatter(name='Shares Outstanding', x=df_rs.columns, y=df_rs.loc["Total common shares outstanding"], marker_color=colors[4], marker_line_color=colors[4]),
            ],
        )
        fig7 = update_layout(fig7, "ratio")
        fig7.write_image(f"{directory}/07 Shares Oustanding - {period_type}.png")

a=1
