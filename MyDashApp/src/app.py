import json
import os

from pymongo import MongoClient

import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
from dash.dependencies import Input, Output

# Initiate app
app = dash.Dash(name=__name__)
server = app.server

# Functions
def clean_dataframe(df):
    try:
        df = df.drop(columns=["TTM"])
    except Exception:
        pass

    for index in df.index:
        try:
            df.loc[index] = df.loc[index].replace('', np.nan)
            df.loc[index] = df.loc[index].apply(lambda x: float(x))
        except Exception:
            df.loc[index] = np.nan
    
    return df

# MongoDB
cluster = MongoClient('mongodb+srv://mongo:KgWIfb4AzqkTyDXb@stockanalysis.f30kw8z.mongodb.net/?retryWrites=true&w=majority')
db = cluster["financial_data"]

# Dropdown
collection = db["overview"]
overview_df = pd.DataFrame(list(collection.find({})))

stock_code_list = overview_df["Stock Code"].to_list()

dropdown_ticker = html.Div([
    dcc.Dropdown(
        options=[{'label': stock_code, 'value': stock_code} for stock_code in stock_code_list],
        value='BBCA',
        id='dropdown_ticker',
        placeholder="Pick a stock code here",
    )
])

# Tabs report type
tabs_report = html.Div([
    dbc.Tabs(id="tabs_report", active_tab='income_statement', children=[
        dbc.Tab(label='Income Statement', tab_id='income_statement'),
        dbc.Tab(label='Balance Sheet', tab_id='balance_sheet'),
        dbc.Tab(label='Cash Flow', tab_id='cash_flow'),
        dbc.Tab(label='Statistics and Ratios', tab_id='ratios'),
    ]),
])

# Tabs timerange stock price
tabs_timerange = html.Div([
    dbc.Tabs(id="tabs_timerange", active_tab='1y', children=[
        dbc.Tab(label='1D', tab_id='1d'),
        dbc.Tab(label='5D', tab_id='5d'),
        dbc.Tab(label='1M', tab_id='1mo'),
        dbc.Tab(label='3M', tab_id='3mo'),
        dbc.Tab(label='6M', tab_id='6mo'),
        dbc.Tab(label='1Y', tab_id='1y'),
        dbc.Tab(label='5Y', tab_id='5y'),
        dbc.Tab(label='10Y', tab_id='10y'),
        dbc.Tab(label='Max', tab_id='max'),
    ]),
])

# Tabs statement type
tabs_statement = html.Div([
    dbc.Tabs(id="tabs_statement", active_tab='yearly', children=[
        dbc.Tab(label='Quarterly', tab_id='quarterly'),
        dbc.Tab(label='Yearly', tab_id='yearly'),
    ]),
])

# Stock price
stock_price = yf.Ticker("BBCA.JK").history(period='5y').Close
fig = go.Figure(data=[go.Scatter(x=stock_price.index, y=stock_price.index, line_smoothing=1.3, line=dict(color='#20c997'))])
fig.update_layout(
    title='Stock price',
)

stock_price_graph = html.Div([
    dcc.Graph(
        id='stock_price_graph',
        figure=fig)
])

# Open json
collection = db["yearly"]

load_json = collection.find_one({"stock_code": "BBCA"})

# Income statement
# Report figure
df_is = pd.DataFrame(load_json["income_statement"])
df_is = clean_dataframe(df_is)

report_fig_is = go.Figure(
    data=[
        go.Bar(name='Revenue', x=df_is.columns, y=df_is.loc["Total revenue"]),
        go.Bar(name='Net Income', x=df_is.columns, y=df_is.loc["Net income"]),
    ]
)
report_fig_is.update_layout(
    title='Revenue & Net Income',
    yaxis=dict(
        title='IDR',
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1, # gap between bars of the same location coordinate.
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template='plotly_white'
)

report_graph_is = html.Div([
    dcc.Graph(
        id='report_graph_is',
        figure=report_fig_is)
])

# YoY growth graph
revenue_growth = df_is.loc["Total revenue"].pct_change()*100
net_income_growth = df_is.loc["Net income"].pct_change()*100
yoy_growth_fig_is = go.Figure(
    data=[
        go.Scatter(x=revenue_growth.index, y=revenue_growth.values, name='Revenue', mode='lines+markers'),
        go.Scatter(x=net_income_growth.index, y=net_income_growth.values, name='Revenue', mode='lines+markers'),
    ]
)

yoy_growth_fig_is.update_layout(
    title='Revenue & Net Income Growth',
    yaxis=dict(
        title='%',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template='plotly_white'
)

yoy_growth_graph_is = html.Div([
    dcc.Graph(
        id='yoy_growth_graph_is',
        figure=yoy_growth_fig_is)
])

# Balance sheet
# Report figure
df_bs = pd.DataFrame(load_json["balance_sheet"])
df_bs = clean_dataframe(df_bs)

report_fig_bs = go.Figure(
    data=[
        go.Bar(x=df_bs.columns, y=df_bs.loc["Total assets"], name='Assets'),
        go.Bar(x=df_bs.columns, y=df_bs.loc["Total liabilities"], name='Liabilities'),
        go.Bar(x=df_bs.columns, y=df_bs.loc["Total equity"], name='Equity'),
    ]
)
report_fig_bs.update_layout(
    title='Balance Sheet',
    yaxis=dict(
        title='IDR',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template='plotly_white'
)

report_graph_bs = html.Div([
    dcc.Graph(
        id='report_graph_bs',
        figure=report_fig_bs)
])

# YoY growth graph
asset_growth = df_bs.loc["Total assets"].pct_change()*100
liabilities_growth = df_bs.loc["Total liabilities"].pct_change()*100
equity_growth = df_bs.loc["Total equity"].pct_change()*100
    
yoy_growth_fig_bs = go.Figure(
    data=[
        go.Scatter(x=asset_growth.index, y=asset_growth.values, name='Assets', mode='lines+markers'),
        go.Scatter(x=liabilities_growth.index, y=liabilities_growth.values, name='Liabilities', mode='lines+markers'),
        go.Scatter(x=equity_growth.index, y=equity_growth.values, name='Equity', mode='lines+markers'),
    ]
)

yoy_growth_fig_bs.update_layout(
    title='Asset, Liabilities, and Equity Growth',
    yaxis=dict(
        title='%',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template='plotly_white'
)

yoy_growth_graph_bs= html.Div([
    dcc.Graph(
        id='yoy_growth_graph_bs',
        figure=yoy_growth_fig_bs)
])

# Cash flow
# Report figure
df_cf = pd.DataFrame(load_json["cash_flow"])
df_cf = clean_dataframe(df_cf)

report_fig_cf = go.Figure(
    data=[
        go.Bar(x=df_cf.columns, y=df_cf.loc["Free cash flow"], name='Free Cash Flow'),
        go.Bar(x=df_cf.columns, y=df_cf.loc["Cash from operating activities"], name='Cash Flow From Operating Activities'),
        go.Bar(x=df_cf.columns, y=df_cf.loc["Cash from investing activities"], name='Cash Flow From Investing Activities'),
        go.Bar(x=df_cf.columns, y=df_cf.loc["Cash from financing activities"], name='Cash Flow From Financing Activities'),
    ]
)
report_fig_cf.update_layout(
    title='Cash Flow',
    yaxis=dict(
        title='IDR',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template='plotly_white'
)

report_graph_cf = html.Div([
    dcc.Graph(
        id='report_graph_cf',
        figure=report_fig_cf)
])

# YoY growth graph
free_cash_flow_growth = df_cf.loc["Free cash flow"].pct_change()*100
cash_flow_operating_growth = df_cf.loc["Cash from operating activities"].pct_change()*100
cash_flow_investing_growth = df_cf.loc["Cash from investing activities"].pct_change()*100
cash_flow_financing_growth = df_cf.loc["Cash from financing activities"].pct_change()*100
    
yoy_growth_fig_cf = go.Figure(
    data=[
        go.Scatter(x=free_cash_flow_growth.index, y=free_cash_flow_growth.values, name='Free Cash Flow', mode='lines+markers'),
        go.Scatter(x=cash_flow_operating_growth.index, y=cash_flow_operating_growth.values, name='Cash Flow From Operating Activities', mode='lines+markers'),
        go.Scatter(x=cash_flow_investing_growth.index, y=cash_flow_investing_growth.values, name='Cash Flow From Investing Activities', mode='lines+markers'),
        go.Scatter(x=cash_flow_financing_growth.index, y=cash_flow_financing_growth.values, name='Cash Flow From Financing Activities', mode='lines+markers'),
    ]
)

yoy_growth_fig_cf.update_layout(
    title='Free Cash Flow Growth',
    yaxis=dict(
        title='%',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    template='plotly_white'
)

yoy_growth_graph_cf= html.Div([
    dcc.Graph(
        id='yoy_growth_graph_cf',
        figure=yoy_growth_fig_cf)
])

# Cash flow
df_ra = pd.DataFrame(load_json["ratios"])
df_ra = clean_dataframe(df_ra)

# Table
# Metrics table
df_metrics = pd.DataFrame(
    columns=["1 year", "3 year", "5 year", "Indicator", "Parameter"],
    index=["Net Income Growth", "Equity Growth", "Free Cash Flow Growth", "Return of Equity", "Return of Assets", "Debt to Equity Ratio", "Current Ratio", "Quick Ratio", "Price to Earnings (PE) Ratio", "Price to Book Value (PBV) Ratio", "Price to Free Cash Flow (PFCF) Ratio"],
    )

for ix, row in df_metrics.iterrows():
    if ix == "Net Income Growth":
        for year in [1, 3, 5]:
            df_metrics.loc[ix, f"{year} year"] = str(round(((df_is.loc["Net income"][-1] - df_is.loc["Net income"][-1-year]) / df_is.loc["Net income"][-1-year] * 100),2)) + " %"
            if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 5:
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 5 %"
    elif ix == "Equity Growth":
        for year in [1, 3, 5]:
            df_metrics.loc[ix, f"{year} year"] = str(round(((df_bs.loc["Total equity"][-1] - df_bs.loc["Total equity"][-1-year]) / df_bs.loc["Total equity"][-1-year] * 100),2)) + " %"
            if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 5:
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 5 %"
    elif ix == "Free Cash Flow Growth":
        for year in [1, 3, 5]:
            df_metrics.loc[ix, f"{year} year"] = str(round(((df_cf.loc["Free cash flow"][-1] - df_cf.loc["Free cash flow"][-1-year]) / df_cf.loc["Free cash flow"][-1-year] * 100),2)) + " %"
            if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 5:
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 5 %"
    elif ix == "Return of Assets":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Return on assets %"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.nanmean(df_ra.loc["Return on assets %"][-1-year:-1]),2)) + " %"
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 10:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 10 %"
    elif ix == "Return of Equity":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Return on equity %"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.nanmean(df_ra.loc["Return on equity %"][-1-year:-1]),2)) + " %"
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 15:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 15 %"
    elif ix == "Debt to Equity Ratio":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Debt to equity ratio"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.nanmean(df_ra.loc["Debt to equity ratio"][-1-year:-1]),2))
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) < 1:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "< 1"
    elif ix == "Current Ratio":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Current ratio"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.nanmean(df_ra.loc["Current ratio"][-1-year:-1]),2))
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 1:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 1"
    elif ix == "Quick Ratio":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Quick ratio"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.nanmean(df_ra.loc["Quick ratio"][-1-year:-1]),2))
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) > 1:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "> 1"
    elif ix == "Price to Earnings (PE) Ratio":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Price to earnings ratio"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.nanmean(df_ra.loc["Price to earnings ratio"][-1-year:-1]),2))
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) < 20:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "< 20"
    elif ix == "Price to Book Value (PBV) Ratio":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Price to book ratio"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.mean(df_ra.loc["Price to book ratio"][-1-year:-1]),2))
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) < 1:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "< 1"
    elif ix == "Price to Free Cash Flow (PFCF) Ratio":
        for year in [1, 3, 5]:
            if not all(pd.isna(df_ra.loc["Price to cash flow ratio"][-1-year:-1])):
                df_metrics.loc[ix, f"{year} year"] = str(round(np.mean(df_ra.loc["Price to cash flow ratio"][-1-year:-1]),2))
                if float(df_metrics.loc[ix, f"{year} year"].replace(' %', '')) < 20:
                    df_metrics.loc[ix, "Indicator"] = '✅'
                else:
                    df_metrics.loc[ix, "Indicator"] = '❌'
        df_metrics.loc[ix, "Parameter"] = "< 20"

df_metrics = df_metrics.reset_index()

metrics_table = html.Div([
    dash_table.DataTable(
        id='metrics_table',
        columns=[{"name": i, "id": i} 
                 for i in df_metrics.columns],
        data=df_metrics.to_dict('records'),
        fixed_columns={'headers': True, 'data': 1 },
        style_table={'minWidth': '100%'},
        style_header={
            'backgroundColor': '#13967d',
            'fontWeight': 'bold',
            'font-family':'Open Sans',
            'textAlign': 'center',
            'color': 'white',
        },
        style_data={'fontSize':12, 'font-family':'Open Sans', 'textAlign': 'center', 'minWidth': '120px', 'width': '120px', 'maxWidth': '120px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        style_cell_conditional=[{'if': {'column_id': 'Variable'}, 'fontWeight': 'bold', 'width': '180px', 'textAlign': 'left'}, {'if': {'column_id': 'Unit'}, 'textAlign': 'center'}],
        style_as_list_view=True,
    ),
], style={"margin-bottom": "60px"}) 

# Data table
df_datatable = df_is.copy()
df_datatable.index = df_datatable.index.rename('Variable')
df_datatable = df_datatable.reset_index()
df_datatable["Unit"] = ""
for index in df_datatable.drop(['Variable', 'Unit'], axis=1).index:
    if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(x) / 1000 if x not in [0, '-'] else 1)) >= 1):
        df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x)/1000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
        df_datatable.loc[index, "Unit"] = "Thousand"
    if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(str(x).replace(' K', '')) / 1000 if x not in [0, '-'] else 1)) >= 1):
        df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x.replace(' K', ''))*1000/1000000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
        df_datatable.loc[index, "Unit"] = "Million"
    if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(str(x).replace(' M', '')) / 1000 if x not in [0, '-'] else 1)) >= 1):
        df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x.replace(' M', ''))*1000000/1000000000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
        df_datatable.loc[index, "Unit"] = "Billion"
    if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(str(x).replace(' B', '')) / 1000 if x not in [0, '-'] else 1)) >= 1):
        df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x.replace(' B', ''))*1000000000/1000000000000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
        df_datatable.loc[index, "Unit"] = "Trillion"

data_table = html.Div([
    dash_table.DataTable(
        id='data_table',
        columns=[{"name": i, "id": i} 
                 for i in df_datatable.columns],
        data=df_datatable.to_dict('records'),
        fixed_columns={'headers': True, 'data': 1 },
        style_table={'minWidth': '100%'},
        style_header={
            'backgroundColor': '#13967d',
            'fontWeight': 'bold',
            'font-family':'Open Sans',
            'textAlign': 'center',
            'color': 'white',
        },
        style_data={'fontSize':12, 'font-family':'Open Sans', 'textAlign': 'right', 'minWidth': '90px', 'width': '90px', 'maxWidth': '90px', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        style_cell_conditional=[{'if': {'column_id': 'Variable'}, 'fontWeight': 'bold', 'width': '180px', 'textAlign': 'left'}, {'if': {'column_id': 'Unit'}, 'textAlign': 'center'}],
        style_as_list_view=True,
    ),
], style={"margin-bottom": "60px"})

app.layout = html.Div([
    html.H1(children='Stock Analyzer Tool', style={'fontSize':36, 'font-family':'Open Sans', 'textAlign': 'center', "margin-top": "30px", 'fontWeight': 'bold'}),
    html.P(children='A dashboard to analyze stocks from IDX (Indonesian Stock Exchange)', style={'fontSize':18, 'font-family':'Open Sans', 'textAlign': 'center', "margin-top": "15px", "margin-bottom": "30px"}),
    dbc.Container(
    children=[
    dbc.Row([
        dbc.Col([
            dropdown_ticker
        ], xs=12, sm=12, md=12, lg=10, xl=10
        )
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            tabs_timerange
        ], xs=12, sm=12, md=12, lg=10, xl=10)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            stock_price_graph
        ], xs=12, sm=12, md=12, lg=10, xl=10)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            metrics_table
        ], xs=10, sm=10, md=10, lg=8, xl=8
        )
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            tabs_statement
        ], xs=12, sm=12, md=12, lg=10, xl=10)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            report_graph_is
        ], xs=12, sm=12, md=12, lg=5, xl=5),
        dbc.Col([
            yoy_growth_graph_is
        ], xs=12, sm=12, md=12, lg=5, xl=5)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            report_graph_bs
        ], xs=12, sm=12, md=12, lg=5, xl=5),
        dbc.Col([
            yoy_growth_graph_bs
        ], xs=12, sm=12, md=12, lg=5, xl=5)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            report_graph_cf
        ], xs=12, sm=12, md=12, lg=5, xl=5),
        dbc.Col([
            yoy_growth_graph_cf
        ], xs=12, sm=12, md=12, lg=5, xl=5)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            tabs_report
        ], xs=12, sm=12, md=12, lg=10, xl=10)
    ], align="center", justify="center"),
    dbc.Row([
        dbc.Col([
            data_table
        ], xs=12, sm=12, md=12, lg=10, xl=10)
    ], align="center", justify="center"),
], fluid=True)
])

@app.callback(
    [
        Output('stock_price_graph', 'figure'),
        Output('report_graph_is', 'figure'),
        Output('yoy_growth_graph_is', 'figure'),
        Output('report_graph_bs', 'figure'),
        Output('yoy_growth_graph_bs', 'figure'),
        Output('report_graph_cf', 'figure'),
        Output('yoy_growth_graph_cf', 'figure'),
        Output('data_table', 'columns'),
        Output('data_table', 'data'),
        Output('metrics_table', 'columns'),
        Output('metrics_table', 'data'),
    ], 
    [
        Input('dropdown_ticker', 'value'),
        Input('tabs_report', 'active_tab'),
        Input('tabs_statement', 'active_tab'),
        Input('tabs_timerange', 'active_tab'),
    ]
)

def update_data(value_dropdown_ticker, value_tabs_report, value_tabs_statement, value_tabs_timerange):
    # Update stockprice
    if value_tabs_timerange == '1d':
        interval = '1m'
    elif value_tabs_timerange == '5d':
        interval = '15m'
    else:
        interval = '1d'
    period = value_tabs_timerange
    stock_price = yf.Ticker(f"{value_dropdown_ticker}.JK").history(period=period, interval=interval).Close
    fig = go.Figure(data=[go.Scatter(x=stock_price.index, y=stock_price.values, line_smoothing=1.3, line=dict(color='#20c997'))])
    fig.update_layout(
        title='Stock price',
    )

    # Open json
    cluster = MongoClient('mongodb+srv://mongo:KgWIfb4AzqkTyDXb@stockanalysis.f30kw8z.mongodb.net/?retryWrites=true&w=majority')
    db = cluster["financial_data"]
    collection = db[f"{value_tabs_statement}"]

    load_json = collection.find_one({"stock_code": value_dropdown_ticker})

    # Income statement
    df_is = pd.DataFrame(load_json["income_statement"])
    df_is = clean_dataframe(df_is)

    if value_tabs_report == "income_statement":
        df_datatable = df_is.copy()
        df_datatable.index = df_datatable.index.rename('Variable')
        df_datatable = df_datatable.reset_index()
    
    report_fig_is = go.Figure(
        data=[
            go.Bar(x=df_is.columns, y=df_is.loc["Total revenue"], name='Revenue'),
            go.Bar(x=df_is.columns, y=df_is.loc["Net income"], name='Net Income'),
        ]
    )
    report_fig_is.update_layout(
        title='Income Statement',
        yaxis=dict(
            title='IDR',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    # YoY growth graph
    revenue_growth = df_is.loc["Total revenue"].pct_change()*100
    net_income_growth = df_is.loc["Net income"].pct_change()*100
    yoy_growth_fig_is = go.Figure(
        data=[
            go.Scatter(x=revenue_growth.index, y=revenue_growth.values, name='Revenue', mode='lines+markers'),
            go.Scatter(x=net_income_growth.index, y=net_income_growth.values, name='Net Income', mode='lines+markers'),
        ]
    )

    yoy_growth_fig_is.update_layout(
        title='Revenue & Net Income Growth',
        yaxis=dict(
            title='%',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    # Balance sheet
    df_bs = pd.DataFrame(load_json["balance_sheet"])
    df_bs = clean_dataframe(df_bs)

    report_fig_bs = go.Figure(
        data=[
            go.Bar(x=df_bs.columns, y=df_bs.loc["Total assets"], name='Assets'),
            go.Bar(x=df_bs.columns, y=df_bs.loc["Total liabilities"], name='Liabilities'),
            go.Bar(x=df_bs.columns, y=df_bs.loc["Total equity"], name='Equity'),
        ]
    )
    report_fig_bs.update_layout(
        title='Balance Sheet',
        yaxis=dict(
            title='IDR',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    if value_tabs_report == "balance_sheet":
        df_datatable = df_bs.copy()
        df_datatable.index = df_datatable.index.rename('Variable')
        df_datatable = df_datatable.reset_index()

    # YoY growth graph
    asset_growth = df_bs.loc["Total assets"].pct_change()*100
    liabilities_growth = df_bs.loc["Total liabilities"].pct_change()*100
    equity_growth = df_bs.loc["Total equity"].pct_change()*100
        
    yoy_growth_fig_bs = go.Figure(
        data=[
            go.Scatter(x=asset_growth.index, y=asset_growth.values, name='Assets', mode='lines+markers'),
            go.Scatter(x=liabilities_growth.index, y=liabilities_growth.values, name='Liabilities', mode='lines+markers'),
            go.Scatter(x=equity_growth.index, y=equity_growth.values, name='Equity', mode='lines+markers'),
        ]
    )

    yoy_growth_fig_bs.update_layout(
        title='Asset, Liabilities, and Equity Growth',
        yaxis=dict(
            title='%',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    df_cf = pd.DataFrame(load_json["cash_flow"])
    df_cf = clean_dataframe(df_cf)

    if value_tabs_report == "cash_flow":
        df_datatable = df_cf.copy()
        df_datatable.index = df_datatable.index.rename('Variable')
        df_datatable = df_datatable.reset_index()

    report_fig_cf = go.Figure(
        data=[
            go.Bar(x=df_cf.columns, y=df_cf.loc["Free cash flow"], name='Free Cash Flow'),
            go.Bar(x=df_cf.columns, y=df_cf.loc["Cash from operating activities"], name='Cash Flow From Operating Activities'),
            go.Bar(x=df_cf.columns, y=df_cf.loc["Cash from investing activities"], name='Cash Flow From Investing Activities'),
            go.Bar(x=df_cf.columns, y=df_cf.loc["Cash from financing activities"], name='Cash Flow From Financing Activities'),
        ]
    )
    report_fig_cf.update_layout(
        title='Cash Flow',
        yaxis=dict(
            title='IDR',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    # YoY growth graph
    free_cash_flow_growth = df_cf.loc["Free cash flow"].pct_change()*100
    cash_flow_operating_growth = df_cf.loc["Cash from operating activities"].pct_change()*100
    cash_flow_investing_growth = df_cf.loc["Cash from investing activities"].pct_change()*100
    cash_flow_financing_growth = df_cf.loc["Cash from financing activities"].pct_change()*100
        
    yoy_growth_fig_cf = go.Figure(
        data=[
            go.Scatter(x=free_cash_flow_growth.index, y=free_cash_flow_growth.values, name='Free Cash Flow', mode='lines+markers'),
            go.Scatter(x=cash_flow_operating_growth.index, y=cash_flow_operating_growth.values, name='Cash Flow From Operating Activities', mode='lines+markers'),
            go.Scatter(x=cash_flow_investing_growth.index, y=cash_flow_investing_growth.values, name='Cash Flow From Investing Activities', mode='lines+markers'),
            go.Scatter(x=cash_flow_financing_growth.index, y=cash_flow_financing_growth.values, name='Cash Flow From Financing Activities', mode='lines+markers'),
        ]
    )

    yoy_growth_fig_cf.update_layout(
        title='Free Cash Flow Growth',
        yaxis=dict(
            title='%',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )

    df_ra = pd.DataFrame(load_json["ratios"])
    df_ra = clean_dataframe(df_ra)

    if value_tabs_report == "ratios":
        df_datatable = df_ra.copy()
        df_datatable.index = df_datatable.index.rename('Variable')
        df_datatable = df_datatable.reset_index()

    # Update data table
    df_datatable["Unit"] = ""
    for index in df_datatable.drop(['Variable', 'Unit'], axis=1).index:
        if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(x) / 1000 if x not in [0, '-'] else 1)) >= 1):
            df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x)/1000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
            df_datatable.loc[index, "Unit"] = "Thousand"
        if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(str(x).replace(' K', '')) / 1000 if x not in [0, '-'] else 1)) >= 1):
            df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x.replace(' K', ''))*1000/1000000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
            df_datatable.loc[index, "Unit"] = "Million"
        if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(str(x).replace(' M', '')) / 1000 if x not in [0, '-'] else 1)) >= 1):
            df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x.replace(' M', ''))*1000000/1000000000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
            df_datatable.loc[index, "Unit"] = "Billion"
        if all(abs(df_datatable.drop(['Variable', 'Unit'], axis=1).loc[index].apply(lambda x: float(str(x).replace(' B', '')) / 1000 if x not in [0, '-'] else 1)) >= 1):
            df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')] = df_datatable.loc[index, np.logical_and(df_datatable.columns != 'Variable', df_datatable.columns != 'Unit')].apply(lambda x: float(x.replace(' B', ''))*1000000000/1000000000000 if x not in ['-'] else '-').apply(lambda x: str(x) if x not in ['-', 'nan', 0] else '-')
            df_datatable.loc[index, "Unit"] = "Trillion"

    table_data = df_datatable.to_dict('records')
    table_columns =[{"name": i, "id": i} for i in df_datatable.columns]

    # Update metrics table
    df_metrics = pd.DataFrame(
        columns=[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}",  "Indicator", "Parameter"],
        index=["Net Income Growth", "Equity Growth", "Free Cash Flow Growth", "Return of Equity", "Return of Assets", "Debt to Equity Ratio", "Current Ratio", "Quick Ratio", "Price to Earnings (PE) Ratio", "Price to Book Value (PBV) Ratio", "Price to Free Cash Flow (PFCF) Ratio"]
        )

    df_metrics.index.name = 'Variable'
    for ix, row in df_metrics.iterrows():
        if ix == "Net Income Growth":
            for year in [1, 3, 5]:
                df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round((abs((df_is.loc["Net income"][-1] - df_is.loc["Net income"][-1-year]) / df_is.loc["Net income"][-1-year] * 100)),2)) + " %"
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 5):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 5 %"
        elif ix == "Equity Growth":
            for year in [1, 3, 5]:
                df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round((abs((df_bs.loc["Total equity"][-1] - df_bs.loc["Total equity"][-1-year]) / df_bs.loc["Total equity"][-1-year] * 100)),2)) + " %"
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 5):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 5 %"
        elif ix == "Free Cash Flow Growth":
            for year in [1, 3, 5]:
                df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round((abs((df_cf.loc["Free cash flow"][-1] - df_cf.loc["Free cash flow"][-1-year]) / df_cf.loc["Free cash flow"][-1-year] * 100)),2)) + " %"
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 5):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 5 %"
        elif ix == "Return of Assets":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Return on assets %"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.nanmean(df_ra.loc["Return on assets %"][-1-year:-1]),2)) + " %"
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 10):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 10 %"
        elif ix == "Return of Equity":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Return on equity %"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.nanmean(df_ra.loc["Return on equity %"][-1-year:-1]),2)) + " %"
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 15):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 15 %"
        elif ix == "Debt to Equity Ratio":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Debt to equity ratio"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.nanmean(df_ra.loc["Debt to equity ratio"][-1-year:-1]),2))
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) < 1):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "< 1"
        elif ix == "Current Ratio":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Current ratio"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.nanmean(df_ra.loc["Current ratio"][-1-year:-1]),2))
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 1):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 1"
        elif ix == "Quick Ratio":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Quick ratio"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.nanmean(df_ra.loc["Quick ratio"][-1-year:-1]),2))
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) > 1):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "> 1"
        elif ix == "Price to Earnings (PE) Ratio":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Price to earnings ratio"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.nanmean(df_ra.loc["Price to earnings ratio"][-1-year:-1]),2))
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) < 20):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "< 20"
        elif ix == "Price to Book Value (PBV) Ratio":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Price to book ratio"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.mean(df_ra.loc["Price to book ratio"][-1-year:-1]),2))
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) < 1):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "< 1"
        elif ix == "Price to Free Cash Flow (PFCF) Ratio":
            for year in [1, 3, 5]:
                if not all(pd.isna(df_ra.loc["Price to cash flow ratio"][-1-year:-1])):
                    df_metrics.loc[ix, f"{year} {value_tabs_statement}"] = str(round(np.mean(df_ra.loc["Price to cash flow ratio"][-1-year:-1]),2))
            if all(df_metrics.loc[ix][[f"1 {value_tabs_statement}", f"3 {value_tabs_statement}", f"5 {value_tabs_statement}"]].apply(lambda x: float(str(x).replace(' %', ''))) < 20):
                df_metrics.loc[ix, "Indicator"] = '✅'
            else:
                df_metrics.loc[ix, "Indicator"] = '❌'
            df_metrics.loc[ix, "Parameter"] = "< 20"

    df_metrics = df_metrics.reset_index()

    metrics_data = df_metrics.to_dict('records')
    metrics_columns =[{"name": i, "id": i} for i in df_metrics.columns]

    return fig, report_fig_is, yoy_growth_fig_is, report_fig_bs, yoy_growth_fig_bs, report_fig_cf, yoy_growth_fig_cf, table_columns, table_data, metrics_columns, metrics_data

if __name__ == '__main__':
    app.run_server(debug=False)