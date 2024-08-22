import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import pickle as pk
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pages.create_data import load
import dash_bootstrap_components as dbc
from pages.create_data import *

DARK_COLOR = 'rgba(0, 0, 0, 0)'
MY_STYLE = {'backgroundColor': 'rgba(207, 207, 207, 207)', 'color': 'black'}

dash.register_page(__name__, path='/PredictiveAnalytics')

layout = html.Div([
dbc.Container([
    dbc.Row([
        dbc.Col(width=1),
        dbc.Col(children=[    
            html.H1('Coming soon....working on it'),
            html.P("For predictive analytics we will model 1) Customer additions, and 2) Customer churn \
           (survival) and 3) Variable Revenue to create a whole set of financial expectations:"),
            html.Ul([
                html.Li("For additions, we will use time series forecasting using a mix of modern \
                        machine learning models as well as traditional ARIMA models"),
                html.Li("For customer churn, we will use maximum likelihood estimation and a Weibul distribution"),
                    ]),
            ]),
        dbc.Col(),
    ], align='center'),]),
    dbc.Row([
        dbc.Col(width=1),
        dbc.Col()

    ], align='center'),])
