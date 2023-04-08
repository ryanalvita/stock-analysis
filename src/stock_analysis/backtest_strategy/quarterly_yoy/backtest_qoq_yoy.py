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
def get_quarter_deadline_tahunan(date):
    year = date.year
    return pd.to_datetime(f'31-03-{year}', format='%d-%m-%Y').normalize()

def get_quarter_deadline_interim(date):
    year = date.year
    if year >= 2020:
        if pd.to_datetime(f'01-09-{year}', format='%d-%m-%Y').normalize() < date <= pd.to_datetime(f'01-12-{year}', format='%d-%m-%Y').normalize():
            return pd.to_datetime(f'31-10-{year}', format='%d-%m-%Y').normalize()
        elif pd.to_datetime(f'01-06-{year}', format='%d-%m-%Y').normalize() < date <= pd.to_datetime(f'01-09-{year}', format='%d-%m-%Y').normalize():
            return pd.to_datetime(f'31-07-{year}', format='%d-%m-%Y').normalize()
        elif pd.to_datetime(f'01-03-{year}', format='%d-%m-%Y').normalize() < date <= pd.to_datetime(f'01-06-{year+1}', format='%d-%m-%Y').normalize():
            return pd.to_datetime(f'30-04-{year}', format='%d-%m-%Y').normalize()
    else:
        if pd.to_datetime(f'01-08-{year}', format='%d-%m-%Y').normalize() < date <= pd.to_datetime(f'01-11-{year}', format='%d-%m-%Y').normalize():
            return pd.to_datetime(f'31-10-{year}', format='%d-%m-%Y').normalize()
        elif pd.to_datetime(f'01-05-{year}', format='%d-%m-%Y').normalize() < date <= pd.to_datetime(f'01-08-{year}', format='%d-%m-%Y').normalize():
            return pd.to_datetime(f'31-07-{year}', format='%d-%m-%Y').normalize()
        elif pd.to_datetime(f'01-02-{year}', format='%d-%m-%Y').normalize() < date <= pd.to_datetime(f'01-05-{year+1}', format='%d-%m-%Y').normalize():
            return pd.to_datetime(f'30-04-{year}', format='%d-%m-%Y').normalize()

def get_quarter_year(date):
    year = date.year
    month = date.month
    if month == 3:
        quarter = 4
        year = year - 1
    elif month == 10:
        quarter = 3
    elif month == 7:
        quarter = 2
    elif month == 4:
        quarter = 1
    return quarter, year

def determine_quarter_col(start_date, date):
    year = date.year
    if (
        datetime(day=1, month=11, year=year - 1)
        <= start_date
        <= datetime(day=31, month=3, year=year)
    ):
        col = f"Q3 {str(year - 1)}"
    elif (
        datetime(day=1, month=4, year=year)
        <= ix
        <= datetime(day=30, month=4, year=year)
    ):
        col = f"Q4 {str(year - 1)}"
    elif (
        datetime(day=1, month=5, year=year)
        <= ix
        <= datetime(day=31, month=7, year=year)
    ):
        col = f"Q1 {str(year)}"
    elif (
        datetime(day=1, month=8, year=year)
        <= ix
        <= datetime(day=31, month=10, year=year)
    ):
        col = f"Q2 {str(year)}"
    elif (
        datetime(day=1, month=11, year=year)
        <= ix
        <= datetime(day=31, month=3, year=year + 1)
    ):
        col = f"Q3 {str(year)}"
    elif (
        datetime(day=1, month=4, year=year + 1)
        <= ix
        <= datetime(day=30, month=4, year=year + 1)
    ):
        col = f"Q4 {str(year)}"

    return col

# Dates
start_date = datetime(year=2008, month=5, day=1)
end_date = datetime.now()

stocks = pd.read_csv("./src/stock_analysis/static/20230402_stocks_list.csv", index_col=0).index.to_list()

for stock in stocks:
    stock = "JKON"
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Get stock price data
    yf_stock = yf.Ticker(f"{stock}.JK")
    stock_price = (
        yf_stock.history(start=start_date, end=end_date, auto_adjust=False)
        .Close.reset_index()
        .set_index("Date")
    )
    stock_price.index = stock_price.tz_localize(None).index
    spikes = stock_price["Close"].quantile(0.9999)
    stock_price = stock_price[stock_price['Close'] <= spikes]
    stock_price = stock_price.resample('D').interpolate(method='linear')

    # Get net income data
    cluster = MongoClient(os.environ["MONGODB_URI"])
    db = cluster["stockbit_data"]
    collection = db["quarterly"]
    data = collection.find_one({"stock_code": stock})
    df = clean_dataframe(pd.DataFrame(data["income_statement"]))

    # Reverse columns
    df = df.loc[:, ::-1]

    # Shift the data by 4 periods (one year)
    df_shifted = df.shift(-4, axis=1)
    growth = (df - df_shifted) / df_shifted * 100
    df.loc["QoQ YoY Net Income Growth"] = growth.loc["Total Net Income Attributable To"]

    # Get release dates data
    cluster = MongoClient(os.environ["MONGODB_PERSONAL_URI"])
    db = cluster["stockbit_data"]
    collection = db["release_dates"]
    release_date = collection.find_one({"stock_code": stock})

    df_release_date = pd.DataFrame(release_date["release_dates"])
    data = pd.DataFrame()

    for keyword in ["Laporan Keuangan Tahunan", "Laporan Keuangan Interim"]:
        _data = df_release_date[df_release_date['title'].str.contains(keyword, case=False)].reset_index(drop=True)

        # Convert the 'date' column to a pandas datetime object
        _data['date'] = pd.to_datetime(_data['date'])

        if "Tahunan" in keyword:
            # Apply the 'get_quarter_deadline' function to the 'quarter' and 'year' columns to get the quarter deadlines
            _data['quarter_deadline'] = _data.apply(lambda row: get_quarter_deadline_tahunan(row["date"]), axis=1)
        
        elif "Interim" in keyword:
            _data['quarter_deadline'] = _data.apply(lambda row: get_quarter_deadline_interim(row['date']), axis=1)
        
        data = pd.concat([data, _data], axis=0)

    # Group the data by quarter and year, and get the earliest release date for each group
    quarterly_data = data.groupby(['quarter_deadline']).agg({'date': 'min'}).reset_index().sort_values('date')
    quarterly_data['quarter'], quarterly_data['year'], = zip(*quarterly_data['quarter_deadline'].apply(get_quarter_year))
    quarterly_data.index = quarterly_data.apply(lambda row: f"Q{row['quarter']} {row['year']}", axis=1)
    quarterly_data = quarterly_data.drop(['year', 'quarter', 'quarter_deadline'], axis=1)
    quarterly_data = quarterly_data.rename(columns={"date": "Release Date"})
    
    df = pd.concat([df, quarterly_data.T])

    # # Calculate PE
    # pe = pd.DataFrame()
    # for ix, values in stock_price.iterrows():
    #     try:
    #         col = determine_quarter_col(start_date, ix)

    #         pe.loc[ix, "pe"] = values.Close / (
    #             float(df.loc["Total Net Income Attributable To", col])
    #             / (float(df.loc["Share Outstanding", col]))
    #         )

    #     except:
    #         pe.loc[ix, "pe"] = np.nan

    # Figure
    # Cut stock price
    stock_price = stock_price[stock_price.index >= min(df.loc["Release Date"].dropna())]

    fig.add_trace(
        go.Scatter(
            x=stock_price.index,
            y=stock_price.Close,
            mode="lines",
            name="Stock Price",
            line=dict(
                color=plotly.colors.qualitative.Plotly[0],
                width=2,
            ),
        ),
    )

    # Marker on price
    fig.add_trace(
        go.Scatter(
            x=stock_price.loc[df.loc["Release Date"].dropna().values].index,
            y=stock_price.loc[df.loc["Release Date"].dropna()]["Close"].values,
            mode="markers",
            name="Stock Price",
            marker=dict(
                size=12,
                color=plotly.colors.qualitative.Plotly[1],
            ),
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.loc["Release Date"],
            y=df.loc["QoQ YoY Net Income Growth"],
            mode="lines+markers",
            name="QoQ YoY Net Income Growth",
            marker=dict(
                size=12,
            ),
            line=dict(
                width=2,
                color=plotly.colors.qualitative.Plotly[2],
            ),
            yaxis="y2"
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.loc["Release Date"],
            y=df.loc["Total Net Income Attributable To"],
            mode="lines+markers",
            name="Net Income",
            marker=dict(
                size=12,
            ),
            line=dict(
                width=2,
                color=plotly.colors.qualitative.Plotly[3],
            ),
            yaxis="y3"
        ),
    )

    # fig.add_trace(
    #     go.Scatter(
    #         x=pe.index,
    #         y=pe.values,
    #         mode="lines",
    #         name="PE Ratio",
    #         line=dict(
    #             width=2,
    #             color=plotly.colors.qualitative.Plotly[4],
    #         ),
    #         yaxis="y4"
    #     ),
    # )

    # Plot finishup
    fig.update_traces(showlegend=False)
    fig.update_layout(
        width=1920,
        height=1080,
        title_text=f"{stock}",
    )

    fig.update_layout(
        yaxis=dict(
            title="Stock Price",
        ),
        yaxis2=dict(
            title="Release Date",
            overlaying="y",
            side="right",
        ),
        yaxis3=dict(
            title="Net Income",
            anchor="y",
            overlaying="y",
            side="right",
            position=1
        ),
        # yaxis4=dict(
        #     title="PE Ratio",
        #     anchor="y",
        #     overlaying="y",
        #     side="right",
        #     position=1
        # ),
    )

    # fig.update_layout(yaxis2=dict(type='log')) # update
    fig.show()
    # fig.write_image(f"{dir}/images/buy_sell_{stock}_{multiple.upper()}.png")
