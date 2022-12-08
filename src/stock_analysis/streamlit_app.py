import numpy as np
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from pymongo import MongoClient
import altair as alt

# MongoDB
cluster = MongoClient(
    "mongodb+srv://mongo:KgWIfb4AzqkTyDXb@stockanalysis.f30kw8z.mongodb.net/?retryWrites=true&w=majority"
)

# Get overview
db_financial_data = cluster["financial_data"]
collection_overview = db_financial_data["overview"]
overview_df = pd.DataFrame(list(collection_overview.find({})))
overview_df = overview_df.sort_values(by="Stock Code")
stock_code_list = overview_df["Stock Code"].to_list()

# Title
st.title("Stock Performance Analyzer Tool")

# Input
# Stock
stock = st.selectbox("Choose any IDX stock:", stock_code_list, index=76)
# Date input
col1, col2 = st.columns(2)
with col1:
    period = st.radio("Period", ("1y", "3y", "5y", "10y", "All"), index=2)
with col2:
    end_date = st.date_input("End date", datetime.now(), max_value=datetime.now())
    end_date = datetime.combine(end_date, datetime.min.time())

if period != "All":
    if period == "1y":
        years = 1
    elif period == "3y":
        years = 3
    elif period == "5y":
        years = 5
    elif period == "10y":
        years = 10
    start_date = end_date - pd.DateOffset(years=years)
else:
    start_date = datetime(year=2008, month=5, day=1)

# Get is, bs, cf
db_stockbit_data = cluster["stockbit_data"]
collection_quarterly = db_stockbit_data["quarterly"]
collection_ttm = db_stockbit_data["ttm"]
data_quarterly = collection_quarterly.find_one({"stock_code": stock})
data_ttm = collection_ttm.find_one({"stock_code": stock})
yf_stock = yf.Ticker(f"{stock}.JK")

df_is = pd.DataFrame(data_ttm["income_statement"])
df_bs = pd.DataFrame(data_quarterly["balance_sheet"])

# Stock ticker
stock_ticker = yf.Ticker(f"{stock}.JK")
splits = stock_ticker.splits

# Get price data from yfinance
stock_price = stock_ticker.history(start=start_date, end=end_date).Close.reset_index()

chart = (
    alt.Chart(stock_price)
    .mark_area(
        line={"color": "#448AFF"},
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="white", offset=0),
                alt.GradientStop(color="#448AFF", offset=1),
            ],
            x1=1,
            x2=1,
            y1=1,
            y2=0,
        ),
    )
    .encode(alt.X("Date:T"), alt.Y("Close:Q"))
)
st.header("Price")
st.altair_chart(chart, use_container_width=True)

pe = pd.DataFrame()
pbv = pd.DataFrame()
net_income_ttm = pd.DataFrame()
book_value_quarterly = pd.DataFrame()
stock_price = stock_price.set_index("Date")
stock_price.index = stock_price.tz_localize(None).index

for ix, values in stock_price.iterrows():
    year = ix.year
    try:
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

        pe.loc[ix, "PE"] = values.Close / float(df_is.loc["EPS (TTM)", col])
        pbv.loc[ix, "PBV"] = values.Close / float(
            df_bs.loc["Book Value Per Share (Quarter)", col]
        )

    except:
        pe.loc[ix, "PE"] = np.nan
        pbv.loc[ix, "PBV"] = np.nan

# Load net income and book value data
net_income_ttm = (
    df_is.loc["Net Income Attributable To"]
    .reset_index()
    .rename(
        {"index": "Period", "Net Income Attributable To": "Net Income (TTM)"}, axis=1
    )
)
book_value_quarterly = (
    df_bs.loc["Total Equity"]
    .reset_index()
    .rename({"index": "Period", "Total Equity": "Book Value (Quarterly)"}, axis=1)
)

# Drop data before start date
year = start_date.year
if (
    datetime(day=1, month=11, year=year - 1)
    <= start_date
    <= datetime(day=31, month=3, year=year)
):
    start_col = f"Q3 {str(year - 1)}"
elif (
    datetime(day=1, month=4, year=year)
    <= start_date
    <= datetime(day=30, month=4, year=year)
):
    start_col = f"Q4 {str(year - 1)}"
elif (
    datetime(day=1, month=5, year=year)
    <= start_date
    <= datetime(day=31, month=7, year=year)
):
    start_col = f"Q1 {str(year)}"
elif (
    datetime(day=1, month=8, year=year)
    <= start_date
    <= datetime(day=31, month=10, year=year)
):
    start_col = f"Q2 {str(year)}"
elif (
    datetime(day=1, month=11, year=year)
    <= start_date
    <= datetime(day=31, month=3, year=year + 1)
):
    start_col = f"Q3 {str(year)}"
elif (
    datetime(day=1, month=4, year=year + 1)
    <= start_date
    <= datetime(day=30, month=4, year=year + 1)
):
    start_col = f"Q4 {str(year)}"

# Drop data after end date
year = end_date.year
if (
    datetime(day=1, month=11, year=year - 1)
    <= end_date
    <= datetime(day=31, month=3, year=year)
):
    end_col = f"Q3 {str(year - 1)}"
elif (
    datetime(day=1, month=4, year=year)
    <= end_date
    <= datetime(day=30, month=4, year=year)
):
    end_col = f"Q4 {str(year - 1)}"
elif (
    datetime(day=1, month=5, year=year)
    <= end_date
    <= datetime(day=31, month=7, year=year)
):
    end_col = f"Q1 {str(year)}"
elif (
    datetime(day=1, month=8, year=year)
    <= end_date
    <= datetime(day=31, month=10, year=year)
):
    end_col = f"Q2 {str(year)}"
elif (
    datetime(day=1, month=11, year=year)
    <= end_date
    <= datetime(day=31, month=3, year=year + 1)
):
    end_col = f"Q3 {str(year)}"
elif (
    datetime(day=1, month=4, year=year + 1)
    <= end_date
    <= datetime(day=30, month=4, year=year + 1)
):
    end_col = f"Q4 {str(year)}"

start_index = net_income_ttm[net_income_ttm["Period"] == start_col].index[0]
end_index = net_income_ttm[net_income_ttm["Period"] == end_col].index[0]
net_income_ttm = net_income_ttm.iloc[end_index:start_index]
book_value_quarterly = book_value_quarterly.iloc[end_index:start_index]

# Adjust pe
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

pe_mean = np.nanmean(pe)
pe_std = np.nanstd(pe)

pbv_mean = np.nanmean(pbv)
pbv_std = np.nanstd(pbv)

pe.index.name = "Date"
pbv.index.name = "Date"

pe = pe.reset_index()
pbv = pbv.reset_index()

pe_chart = alt.Chart(pe).mark_line(color="#26C6DA").encode(x="Date", y="PE")
pbv_chart = alt.Chart(pbv).mark_line(color="#26C6DA").encode(x="Date", y="PBV")

pe_mean_chart = (
    alt.Chart(pd.DataFrame({"PE Mean": pe_mean}, index=[0]))
    .mark_rule()
    .encode(y="PE Mean")
)
pe_mean_sd_1_chart = (
    alt.Chart(pd.DataFrame({"PE +1 Std": pe_mean + pe_std}, index=[0]))
    .mark_rule()
    .encode(y="PE +1 Std")
)
pe_mean_sd_2_chart = (
    alt.Chart(pd.DataFrame({"PE +2 Std": pe_mean + 2 * pe_std}, index=[0]))
    .mark_rule()
    .encode(y="PE +2 Std")
)
pe_mean_sd_min_1_chart = (
    alt.Chart(pd.DataFrame({"PE -1 Std": pe_mean - pe_std}, index=[0]))
    .mark_rule()
    .encode(y="PE -1 Std")
)
pe_mean_sd_min_2_chart = (
    alt.Chart(pd.DataFrame({"PE -2 Std": pe_mean - 2 * pe_std}, index=[0]))
    .mark_rule()
    .encode(y="PE -2 Std")
)

pbv_mean_chart = (
    alt.Chart(pd.DataFrame({"PBV Mean": pbv_mean}, index=[0]))
    .mark_rule()
    .encode(y="PBV Mean")
)
pbv_mean_sd_1_chart = (
    alt.Chart(pd.DataFrame({"PBV +1 Std": pbv_mean + pbv_std}, index=[0]))
    .mark_rule()
    .encode(y="PBV +1 Std")
)
pbv_mean_sd_2_chart = (
    alt.Chart(pd.DataFrame({"PBV +2 Std": pbv_mean + 2 * pbv_std}, index=[0]))
    .mark_rule()
    .encode(y="PBV +2 Std")
)
pbv_mean_sd_min_1_chart = (
    alt.Chart(pd.DataFrame({"PBV -1 Std": pbv_mean - pbv_std}, index=[0]))
    .mark_rule()
    .encode(y="PBV -1 Std")
)
pbv_mean_sd_min_2_chart = (
    alt.Chart(pd.DataFrame({"PBV -2 Std": pbv_mean - 2 * pbv_std}, index=[0]))
    .mark_rule()
    .encode(y="PBV -2 Std")
)

pe_layer_chart = (
    pe_chart
    + pe_mean_chart
    + pe_mean_sd_1_chart
    + pe_mean_sd_2_chart
    + pe_mean_sd_min_1_chart
    + pe_mean_sd_min_2_chart
)
pe_layer_chart = pe_layer_chart.encode(
    y=alt.Y(
        title="PE",
        scale=alt.Scale(
            domain=(
                pe_mean - 4 * pe_std,
                pe_mean + 4 * pe_std,
            )
        ),
    )
)

pbv_layer_chart = (
    pbv_chart
    + pbv_mean_chart
    + pbv_mean_sd_1_chart
    + pbv_mean_sd_2_chart
    + pbv_mean_sd_min_1_chart
    + pbv_mean_sd_min_2_chart
)
pbv_layer_chart = pbv_layer_chart.encode(
    y=alt.Y(
        title="PBV",
        scale=alt.Scale(
            domain=(
                pbv_mean - 4 * pbv_std,
                pbv_mean + 4 * pbv_std,
            )
        ),
    )
)

st.header("Valuation")
st.altair_chart(
    pe_layer_chart,
    use_container_width=True,
)
st.altair_chart(
    pbv_layer_chart,
    use_container_width=True,
)

net_income_chart = (
    alt.Chart(net_income_ttm)
    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color="#FF9800")
    .encode(
        alt.X(
            "Period:O",
            sort=net_income_ttm["Period"]
            .reindex(index=net_income_ttm["Period"].index[::-1])
            .to_list(),
        ),
        y="Net Income (TTM):Q",
    )
)

book_value_chart = (
    alt.Chart(book_value_quarterly)
    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color="#FF9800")
    .encode(
        alt.X(
            "Period:O",
            sort=book_value_quarterly["Period"]
            .reindex(index=book_value_quarterly["Period"].index[::-1])
            .to_list(),
        ),
        y="Book Value (Quarterly):Q",
    )
)

st.header("Net Income")
st.altair_chart(
    net_income_chart,
    use_container_width=True,
)
st.header("Book Value")
st.altair_chart(
    book_value_chart,
    use_container_width=True,
)
