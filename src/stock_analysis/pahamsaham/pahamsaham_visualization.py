import os
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
import plotly.graph_objs as go
import numpy as np
import yfinance as yf

# Functions
def clean_dataframe(df):
    most_recent_period = df.columns[0].split(" ")[0]
    most_recent_year = df.columns[0].split(" ")[-1]

    years = [
        year for year in range(int(most_recent_year) - 5, int(most_recent_year) + 1)
    ]
    columns = [most_recent_period + f" {year}" for year in years]

    df = df[columns]

    for index in df.index:
        df.loc[index] = df.loc[index].apply(lambda x: x.replace("%", ""))
        df.loc[index] = df.loc[index].apply(lambda x: np.nan if x == "" else x)
        df.loc[index] = df.loc[index].apply(lambda x: float(x))

    return df


def update_layout(fig, figtype):
    if figtype.lower() == "percentage":
        fig.update_layout(yaxis=dict(title="%", title_standoff=0))
    elif figtype == "ratio" or figtype == "valuation":
        fig.update_layout(
            yaxis=dict(title="", title_standoff=0),
        )
    elif figtype == "price":
        fig.update_layout(
            yaxis=dict(title="IDR", title_standoff=0),
        )
    elif figtype == "basic":
        fig.update_layout(
            yaxis=dict(title="IDR", title_standoff=0),
            barmode="group",
            bargap=0.4,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig.update_yaxes(tickformat=".2s")

    elif figtype == "shares_outstanding":
        fig.update_layout(
            yaxis=dict(title="IDR", title_standoff=0),
            barmode="group",
            bargap=0.4,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
    fig.update_layout(
        showlegend=False,
        # legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        font=dict(
            family="Helvetica",
            size=12,
        ),
        width=900,
        height=175,
        margin=dict(l=25, r=25, b=25, t=25, pad=4),
        template="ggplot2",
    )
    if figtype == "valuation" or figtype == "price":
        fig.update_layout(
            showlegend=False,
            # legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
            font=dict(
                family="Helvetica",
                size=12,
            ),
            width=900,
            height=250,
            margin=dict(l=25, r=25, b=25, t=25, pad=4),
            template="ggplot2",
        )
    if figtype == "shareholders":
        fig.update_layout(
            showlegend=False,
            # legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
            font=dict(
                family="Helvetica",
                size=12,
            ),
            width=350,
            height=350,
            margin=dict(l=25, r=25, b=25, t=25, pad=4),
            template="ggplot2",
        )
    if figtype == "revenue_stream":
        fig.update_layout(
            showlegend=False,
            # legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
            font=dict(
                family="Helvetica",
                size=12,
            ),
            width=450,
            height=450,
            margin=dict(l=25, r=25, b=25, t=25, pad=4),
            template="ggplot2",
        )

    return fig


# Initialize MongoDB
cluster = MongoClient(os.environ["MONGODB_URI"])
db = cluster["stockbit_data"]

# Determine stock
stock = "BBRI"

# Determine color scheme
colors = ["#448AFF", "#FF9800", "#26C6DA", "#B388FF", "#3D4750", "#BABABA"]

# Define date
datenow_str = datetime.strftime(datetime.now(), "%Y%m%d")

# Create folder if it is not exist
directory = f"images/{stock}/{datenow_str}"
if not os.path.exists(directory):
    os.makedirs(directory)

collection_ytd = db["ytd"]
data_ytd = collection_ytd.find_one({"stock_code": stock})

collection_quarterly = db["quarterly"]
data_quarterly = collection_quarterly.find_one({"stock_code": stock})

collection_ttm = db["ttm"]
data_ttm = collection_ttm.find_one({"stock_code": stock})

df_is = clean_dataframe(pd.DataFrame(data_ttm["income_statement"]))
df_bs = clean_dataframe(pd.DataFrame(data_quarterly["balance_sheet"]))
df_cf = clean_dataframe(pd.DataFrame(data_ttm["cash_flow"]))

df_is_ttm = pd.DataFrame(data_ttm["income_statement"])
for index in df_is_ttm.index:
    df_is_ttm.loc[index] = df_is_ttm.loc[index].apply(lambda x: x.replace("%", ""))
    df_is_ttm.loc[index] = df_is_ttm.loc[index].apply(
        lambda x: np.nan if x == "" else x
    )
    df_is_ttm.loc[index] = df_is_ttm.loc[index].apply(lambda x: float(x))

df_bs_quarterly = pd.DataFrame(data_quarterly["balance_sheet"])
for index in df_bs_quarterly.index:
    df_bs_quarterly.loc[index] = df_bs_quarterly.loc[index].apply(
        lambda x: x.replace("%", "")
    )
    df_bs_quarterly.loc[index] = df_bs_quarterly.loc[index].apply(
        lambda x: np.nan if x == "" else x
    )
    df_bs_quarterly.loc[index] = df_bs_quarterly.loc[index].apply(lambda x: float(x))


# Add profit margin for df_is
df_is.loc["Gross margin (TTM)"] = (
    df_is.loc["Gross Profit"] / df_is.loc["Total Revenue"] * 100
)
df_is.loc["Operating margin (TTM)"] = (
    df_is.loc["Income From Operations"] / df_is.loc["Total Revenue"] * 100
)
df_is.loc["Net margin (TTM)"] = (
    df_is.loc["Net Income Attributable To"] / df_is.loc["Total Revenue"] * 100
)

# 01 - Revenue & Net Income
fig1 = go.Figure(
    data=[
        go.Bar(
            name="Revenue",
            x=df_is.columns,
            y=df_is.loc["Total Revenue"],
            marker_color=colors[0],
        ),
        go.Bar(
            name="Net Income",
            x=df_is.columns,
            y=df_is.loc["Net Income Attributable To"],
            marker_color=colors[1],
        ),
    ],
)
fig1 = update_layout(fig1, "basic")
fig1.write_image(f"{directory}/01 Revenue & Net Income.png")

# 02 - Assets, Liabilites, and Equity
fig2 = go.Figure(
    data=[
        go.Bar(
            name="Assets",
            x=df_bs.columns,
            y=df_bs.loc["Total Assets"],
            marker_color=colors[0],
        ),
        go.Bar(
            name="Liabilities",
            x=df_bs.columns,
            y=df_bs.loc["Total Liabilities"],
            marker_color=colors[1],
        ),
        go.Bar(
            name="Equity",
            x=df_bs.columns,
            y=df_bs.loc["Total Equity"],
            marker_color=colors[2],
        ),
    ],
)
fig2 = update_layout(fig2, "basic")
fig2.write_image(f"{directory}/02 - Assets, Liabilites, and Equity.png")

# 03 - Cash flow from operating, investing, and financing activities
fig3 = go.Figure(
    data=[
        go.Bar(
            name="Operating",
            x=df_cf.columns,
            y=df_cf.loc["Cash Flows From Operating Activities"],
            marker_color=colors[0],
        ),
        go.Bar(
            name="Investing",
            x=df_cf.columns,
            y=df_cf.loc["Cash Flows From Investing Activities"],
            marker_color=colors[1],
        ),
        go.Bar(
            name="Financing",
            x=df_cf.columns,
            y=df_cf.loc["Cash Flows From Financing Activities"],
            marker_color=colors[2],
        ),
    ],
)
fig3 = update_layout(fig3, "basic")
fig3.write_image(
    f"{directory}/03 - Cash Flow from Operating, Investing, and Financing Activities.png"
)

# 04 Profitability
# 04a Profit Margin
fig4a = go.Figure(
    data=[
        go.Scatter(
            name="Gross Margin",
            x=df_is.columns,
            y=df_is.loc["Gross margin (TTM)"],
            marker_color=colors[0],
            marker_line_color=colors[0],
        ),
        go.Scatter(
            name="Operating Margin",
            x=df_is.columns,
            y=df_is.loc["Operating margin (TTM)"],
            marker_color=colors[1],
            marker_line_color=colors[1],
        ),
        go.Scatter(
            name="Net margin",
            x=df_is.columns,
            y=df_is.loc["Net margin (TTM)"],
            marker_color=colors[2],
            marker_line_color=colors[2],
        ),
    ],
)
fig4a = update_layout(fig4a, "percentage")
fig4a.write_image(f"{directory}/04a Profitability (Margin).png")

# 04b Return
fig4b = go.Figure(
    data=[
        go.Scatter(
            name="ROE",
            x=df_is.columns,
            y=df_is.loc["Return on Equity (TTM)"],
            marker_color=colors[0],
            marker_line_color=colors[0],
        ),
        go.Scatter(
            name="ROA",
            x=df_is.columns,
            y=df_is.loc["Return on Assets (TTM)"],
            marker_color=colors[1],
            marker_line_color=colors[1],
        ),
    ],
)
fig4b = update_layout(fig4b, "percentage")
fig4b.write_image(f"{directory}/04b Profitability (Return).png")

# 05 Solvability
# 05a Liquidity Ratio
fig5a = go.Figure(
    data=[
        go.Scatter(
            name="Quick Ratio",
            x=df_bs.columns,
            y=df_bs.loc["Quick Ratio (Quarter)"],
            marker_color=colors[0],
            marker_line_color=colors[0],
        ),
        go.Scatter(
            name="Current Ratio",
            x=df_bs.columns,
            y=df_bs.loc["Current Ratio (Quarter)"],
            marker_color=colors[1],
            marker_line_color=colors[1],
        ),
    ],
)
fig5a = update_layout(fig5a, "ratio")
fig5a.write_image(f"{directory}/05a Solvability (Liquidity Ratio).png")

# 05b Solvency Ratio
fig5b = go.Figure(
    data=[
        go.Scatter(
            name="Debt to Equity Ratio",
            x=df_bs.columns,
            y=df_bs.loc["Debt to Equity Ratio (Quarter)"],
            marker_color=colors[0],
            marker_line_color=colors[0],
        ),
    ],
)
fig5b = update_layout(fig5b, "ratio")
fig5b.write_image(f"{directory}/05b Solvability (Solvency Ratio).png")

# 6 Valuation
def determine_pe_pbv():
    pe = pd.Series()
    pbv = pd.Series()

    # Stock ticker
    stock_ticker = yf.Ticker(f"{stock}.JK")
    splits = stock_ticker.splits

    # Get price data from yfinance
    stock_price = stock_ticker.history(
        start=datetime.now() - pd.DateOffset(years=5), end=datetime.now()
    ).Close.reset_index()

    stock_price = stock_price.set_index("Date")
    stock_price.index = stock_price.tz_localize(None).index

    # Adjust custom splits because sometimes it is not working properly
    splits = splits.rename(
        index={
            splits.index[1]: pd.Timestamp(
                year=2017, month=10, day=31, tz="Asia/Jakarta"
            )
        }
    )

    for ix, values in stock_price.iterrows():
        year = ix.year
        try:
            if (
                datetime(day=1, month=11, year=year - 1)
                <= ix
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

            pe[ix] = values.Close / float(df_is_ttm.loc["EPS (TTM)", col])
            pbv[ix] = values.Close / float(
                df_bs_quarterly.loc["Book Value Per Share (Quarter)", col]
            )

        except:
            pe[ix] = np.nan
            pbv[ix] = np.nan

    # Adjust pe & pbv based on splits
    for ix, values in splits.tz_localize(None).items():
        year = ix.year
        if (
            datetime(day=1, month=11, year=year - 1)
            <= ix
            <= datetime(day=31, month=3, year=year)
        ):
            adjust_date = datetime(day=30, month=4, year=year)
        elif (
            datetime(day=1, month=4, year=year)
            <= ix
            <= datetime(day=30, month=4, year=year)
        ):
            adjust_date = datetime(day=31, month=7, year=year)
        elif (
            datetime(day=1, month=5, year=year)
            <= ix
            <= datetime(day=31, month=7, year=year)
        ):
            adjust_date = datetime(day=31, month=10, year=year)
        elif (
            datetime(day=1, month=8, year=year)
            <= ix
            <= datetime(day=31, month=10, year=year)
        ):
            adjust_date = datetime(day=31, month=3, year=year + 1)
        elif (
            datetime(day=1, month=11, year=year)
            <= ix
            <= datetime(day=31, month=3, year=year + 1)
        ):
            adjust_date = datetime(day=30, month=4, year=year + 1)
        elif (
            datetime(day=1, month=4, year=year + 1)
            <= ix
            <= datetime(day=30, month=4, year=year + 1)
        ):
            adjust_date = datetime(day=31, month=7, year=year + 1)

        pe[pe.index <= adjust_date] = pe[pe.index <= adjust_date].values * values
        pbv[pbv.index <= adjust_date] = pbv[pbv.index <= adjust_date].values * values

    return pe, pbv


def determine_mean_std(data):
    mean = np.nanmean(data)
    std = np.nanstd(data)

    std_plus_1 = mean + 1 * std
    std_plus_2 = mean + 2 * std
    std_minus_1 = mean - 1 * std
    std_minus_2 = mean - 2 * std

    return mean, std_plus_1, std_plus_2, std_minus_1, std_minus_2


pe, pbv = determine_pe_pbv()
(
    pe_mean,
    pe_std_plus_1,
    pe_std_plus_2,
    pe_std_minus_1,
    pe_std_minus_2,
) = determine_mean_std(pe)
(
    pbv_mean,
    pbv_std_plus_1,
    pbv_std_plus_2,
    pbv_std_minus_1,
    pbv_std_minus_2,
) = determine_mean_std(pbv)

# 6a PE Valuation
fig6a = go.Figure(
    data=[
        go.Scatter(
            name="PE Ratio",
            x=pe.index,
            y=pe.values,
            marker_color=colors[0],
            marker_line_color=colors[0],
        ),
    ],
)

fig6a.add_hline(
    y=pe_mean,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="Mean",
    annotation_font_size=10,
)
fig6a.add_hline(
    y=pe_std_plus_1,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="+1 Stdev",
    annotation_font_size=10,
)
fig6a.add_hline(
    y=pe_std_plus_2,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="+2 Stdev",
    annotation_font_size=10,
)
fig6a.add_hline(
    y=pe_std_minus_1,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="-1 Stdev",
    annotation_font_size=10,
)
fig6a.add_hline(
    y=pe_std_minus_2,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="-2 Stdev",
    annotation_font_size=10,
)
fig6a = update_layout(fig6a, "valuation")
fig6a.write_image(f"{directory}/06a Valuation (PE).png")

# 6a PE Valuation
fig6b = go.Figure(
    data=[
        go.Scatter(
            name="PBV Ratio",
            x=pbv.index,
            y=pbv.values,
            marker_color=colors[1],
            marker_line_color=colors[1],
        ),
    ],
)
fig6b.add_hline(
    y=pbv_mean,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="Mean",
    annotation_font_size=10,
)
fig6b.add_hline(
    y=pbv_std_plus_1,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="+1 Stdev",
    annotation_font_size=10,
)
fig6b.add_hline(
    y=pbv_std_plus_2,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="+2 Stdev",
    annotation_font_size=10,
)
fig6b.add_hline(
    y=pbv_std_minus_1,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="-1 Stdev",
    annotation_font_size=10,
)
fig6b.add_hline(
    y=pbv_std_minus_2,
    line_dash="dot",
    line_color="black",
    line_width=1,
    annotation_text="-2 Stdev",
    annotation_font_size=10,
)
fig6b = update_layout(fig6b, "valuation")
fig6b.write_image(f"{directory}/06b Valuation (PBV).png")

# 7 Shares outstanding
# Delete period in the df_bs only for shares outstanding
rename_columns = {col: col[-4:] for col in df_bs}

df_bs = df_bs.rename(columns=rename_columns)

fig7 = go.Figure(
    data=[
        go.Bar(
            name="Shares Outstanding",
            x=df_bs.columns,
            y=df_bs.loc["Share Outstanding"],
            marker_color=colors[0],
        ),
    ],
)
fig7 = update_layout(fig7, "shares_outstanding")
fig7.write_image(f"{directory}/07 Shares Oustanding.png")

# 8 Shareholders
shareholders = pd.read_excel(
    "src/stock_analysis/input_piechart.xlsx", sheet_name="Shareholders"
)

labels = shareholders["Pemegang Saham"]
values = shareholders["Persentase"]

# Use `hole` to create a donut-like pie chart
fig8 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
fig8.update_traces(marker=dict(colors=colors), textinfo="none")
fig8 = update_layout(fig8, "shareholders")
fig8.write_image(f"{directory}/08 Shareholders.png")

# 9 Revenue Stream
revenue_stream = pd.read_excel(
    "src/stock_analysis/input_piechart.xlsx", sheet_name="RevenueStream"
)
revenue_stream = revenue_stream.drop(
    revenue_stream[revenue_stream["Nama"] == "Total"].index, axis=0
)

labels = revenue_stream["Nama"]
values = revenue_stream["Persentase"]

# Use `hole` to create a donut-like pie chart
fig9 = go.Figure(data=[go.Pie(labels=labels, values=values)])
fig9.update_traces(marker=dict(colors=colors), textinfo="none")
fig9 = update_layout(fig9, "revenue_stream")
fig9.write_image(f"{directory}/09 Revenue Stream.png")


# Stock price
stock_ticker = yf.Ticker(f"{stock}.JK")
end_date = datetime.now()
start_date = end_date - pd.DateOffset(years=1)

# Get price data from yfinance
stock_price = stock_ticker.history(
    start=start_date, end=end_date, auto_adjust=False
).Close.reset_index()
fig10 = go.Figure(data=[go.Scatter(x=stock_price["Date"], y=stock_price["Close"])])
fig10.update_traces(marker_color=colors[1], marker_line_color=colors[1])
fig10 = update_layout(fig10, "price")
fig10.write_image(f"{directory}/10 Share Price.png")

a = 1
