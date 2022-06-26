import json
from os import walk

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
from dash.dependencies import Input, Output
from soupsieve import select


# Functions
def clean_dataframe(df):

    try:
        df = df.drop(columns=["TTM"])
    except:
        pass

    for index in df.index:
        try:
            df.loc[index] = df.loc[index].replace('', np.nan)
            df.loc[index] = df.loc[index].apply(lambda x: float(x))
        except:
            df.loc[index] = np.nan
    
    return df

# Initiate app
app = dash.Dash(__name__)

# Dropdown
stock_code_list = []
for (dirpaths, dirnames, filenames) in walk ('./results/tradingview/yearly'):
    stock_code_list.extend([filename[0:4] for filename in filenames])

dropdown_ticker = html.Div([
        dcc.Dropdown(
            options=[{'label': stock_code, 'value': stock_code} for stock_code in stock_code_list],
            value='BBCA',
            id='dropdown_ticker',
        )
    ])

# Tabs report type
tabs_report = html.Div([
    dbc.Tabs(id="tabs_report", active_tab='income_statement', children=[
        dbc.Tab(label='Income Statement', tab_id='income_statement'),
        dbc.Tab(label='Balance Sheet', tab_id='balance_sheet'),
        dbc.Tab(label='Cash Flow', tab_id='cash_flow'),
    ]),
])

# Tabs timerange stock price
tabs_timerange = html.Div([
    dbc.Tabs(id="tabs_timerange", active_tab='1mo', children=[
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

stock_price_graph = html.Div([
    dcc.Graph(
        id='stock_price_graph',
        figure=fig)
])

# Report figure
with open(f'results/tradingview/yearly/BBCA.json', 'rb') as f:
    contents = f.read()
    load_json = json.loads(contents.decode('ISO-8859-1'))
    df = pd.DataFrame(load_json["income_statement"]["data"], index=load_json["income_statement"]["index"], columns=load_json["income_statement"]["columns"])
    df = clean_dataframe(df)

report_fig = go.Figure(
    data=[
        go.Bar(name='Revenue', x=df.columns, y=df.loc["Total revenue"]),
        go.Bar(name='Net Income', x=df.columns, y=df.loc["Net income"]),
    ]
)
report_fig.update_layout(
    title='Revenue & Net Income',
    yaxis=dict(
        title='IDR',
    ),
    barmode='group',
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)

report_graph = html.Div([
    dcc.Graph(
        id='report_graph',
        figure=report_fig)
])

# YoY growth graph
revenue_growth = df.loc["Total revenue"].pct_change()*100
net_income_growth = df.loc["Net income"].pct_change()*100
yoy_growth_fig = go.Figure(
    data=[
        go.Scatter(x=revenue_growth.index, y=revenue_growth.values, name='Revenue', mode='lines+markers'),
        go.Scatter(x=net_income_growth.index, y=net_income_growth.values, name='Revenue', mode='lines+markers'),
    ]
)

yoy_growth_fig.update_layout(
    title='Revenue & Net Income Growth',
)

yoy_growth_graph = html.Div([
    dcc.Graph(
        id='yoy_growth_graph',
        figure=yoy_growth_fig)
])

# Table
df_datatable = df.copy()
df_datatable.index = df_datatable.index.rename('Parameter')
df_datatable = df_datatable.reset_index()
data_table = html.Div([
    dbc.Table.from_dataframe(
        df_datatable, 
        striped=True, 
        bordered=True, 
        hover=True,
        size='lg',
        color='default',
        id='data_table'),
])

app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            dropdown_ticker
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            tabs_timerange
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            stock_price_graph
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            tabs_report
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            tabs_statement
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            report_graph
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            yoy_growth_graph
        ], width=12, align="center")
    ]),
    dbc.Row([
        dbc.Col([
            data_table
        ], width=12, align="center")
    ]),
])

@app.callback(
    [
        Output('stock_price_graph', 'figure'),
        Output('report_graph', 'figure'),
        Output('yoy_growth_graph', 'figure'),
        Output('data_table', 'children'),
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
        interval = '30m'
    else:
        interval = '1d'
    period = value_tabs_timerange
    stock_price = yf.Ticker(f"{value_dropdown_ticker}.JK").history(period=period, interval=interval).Close
    fig = go.Figure(data=[go.Scatter(x=stock_price.index, y=stock_price.values, line_smoothing=1.3, line=dict(color='#20c997'))])

    # Update table
    with open(f'results/tradingview/{value_tabs_statement}/{value_dropdown_ticker}.json', 'rb') as f:
        contents = f.read()
        load_json = json.loads(contents.decode('ISO-8859-1'))

        if value_tabs_report == 'income_statement':
            df = pd.DataFrame(load_json["income_statement"]["data"], index=load_json["income_statement"]["index"], columns=load_json["income_statement"]["columns"])
            df = clean_dataframe(df)
            
            report_fig = go.Figure(
                data=[
                    go.Bar(x=df.columns, y=df.loc["Total revenue"], name='Revenue'),
                    go.Bar(x=df.columns, y=df.loc["Net income"], name='Net Income'),
                ]
            )
            report_fig.update_layout(
                title='Income Statement',
            )

            # YoY growth graph
            revenue_growth = df.loc["Total revenue"].pct_change()*100
            net_income_growth = df.loc["Net income"].pct_change()*100
            yoy_growth_fig = go.Figure(
                data=[
                    go.Scatter(x=revenue_growth.index, y=revenue_growth.values, name='Revenue', mode='lines+markers'),
                    go.Scatter(x=net_income_growth.index, y=net_income_growth.values, name='Net Income', mode='lines+markers'),
                ]
            )

            yoy_growth_fig.update_layout(
                title='Revenue & Net Income Growth'
            )

        elif value_tabs_report == 'balance_sheet':
            df = pd.DataFrame(load_json["balance_sheet"]["data"], index=load_json["balance_sheet"]["index"], columns=load_json["balance_sheet"]["columns"])
            df = clean_dataframe(df)

            report_fig = go.Figure(
                data=[
                    go.Bar(x=df.columns, y=df.loc["Total assets"], name='Assets'),
                    go.Bar(x=df.columns, y=df.loc["Total liabilities"], name='Liabilities'),
                    go.Bar(x=df.columns, y=df.loc["Total equity"], name='Equity'),
                ]
            )
            report_fig.update_layout(
                title='Balance Sheet',
            )

            # YoY growth graph
            asset_growth = df.loc["Total assets"].pct_change()*100
            liabilities_growth = df.loc["Total liabilities"].pct_change()*100
            equity_growth = df.loc["Total equity"].pct_change()*100
             
            yoy_growth_fig = go.Figure(
                data=[
                    go.Scatter(x=asset_growth.index, y=asset_growth.values, name='Assets', mode='lines+markers'),
                    go.Scatter(x=liabilities_growth.index, y=liabilities_growth.values, name='Liabilities', mode='lines+markers'),
                    go.Scatter(x=equity_growth.index, y=equity_growth.values, name='Equity', mode='lines+markers'),
                ]
            )

            yoy_growth_fig.update_layout(
                title='Asset, Liabilities, and Equity Growth',
                yaxis=dict(
                    title='%',
                )
            )

        elif value_tabs_report == 'cash_flow':
            df = pd.DataFrame(load_json["cash_flow"]["data"], index=load_json["cash_flow"]["index"], columns=load_json["cash_flow"]["columns"])
            df = clean_dataframe(df)

            report_fig = go.Figure(
                data=[
                    go.Bar(x=df.columns, y=df.loc["Free cash flow"], name='Free Cash Flow'),
                    go.Bar(x=df.columns, y=df.loc["Cash from operating activities"], name='Cash Flow From Operating Activities'),
                    go.Bar(x=df.columns, y=df.loc["Cash from investing activities"], name='Cash Flow From Investing Activities'),
                    go.Bar(x=df.columns, y=df.loc["Cash from financing activities"], name='Cash Flow From Financing Activities'),
                ]
            )
            report_fig.update_layout(
                title='Cash Flow',
            )

            # YoY growth graph
            free_cash_flow_growth = df.loc["Free cash flow"].pct_change()*100
            cash_flow_operating_growth = df.loc["Cash from operating activities"].pct_change()*100
            cash_flow_investing_growth = df.loc["Cash from investing activities"].pct_change()*100
            cash_flow_financing_growth = df.loc["Cash from financing activities"].pct_change()*100
             
            yoy_growth_fig = go.Figure(
                data=[
                    go.Scatter(x=free_cash_flow_growth.index, y=free_cash_flow_growth.values, name='Free Cash Flow', mode='lines+markers'),
                    go.Scatter(x=cash_flow_operating_growth.index, y=cash_flow_operating_growth.values, name='Cash Flow From Operating Activities', mode='lines+markers'),
                    go.Scatter(x=cash_flow_investing_growth.index, y=cash_flow_investing_growth.values, name='Cash Flow From Investing Activities', mode='lines+markers'),
                    go.Scatter(x=cash_flow_financing_growth.index, y=cash_flow_financing_growth.values, name='Cash Flow From Financing Activities', mode='lines+markers'),
                ]
            )

            yoy_growth_fig.update_layout(
                title='Free Cash Flow Growth',
                yaxis=dict(
                    title='%',
                )
            )
    
    df_datatable = df.copy()
    df_datatable.index = df_datatable.index.rename('Parameter')
    df_datatable = df_datatable.reset_index()

    return [fig, report_fig, yoy_growth_fig, dbc.Table.from_dataframe(df_datatable, striped=True, bordered=True, hover=True, size='lg', color='default')]

if __name__ == '__main__':
    app.run_server(debug=False)

