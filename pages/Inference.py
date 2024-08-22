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

dash.register_page(__name__, path='/Inference')

layout = html.Div([
dbc.Container([
    dbc.Row([
        dbc.Col(width=1),
        dbc.Col(children=[    
            html.H1('Coming soon....working on it'),
            html.P("For inference, we will look at the factors that influence customer behavior:"),
            html.Ul([
                html.Li("For additions we'll look at ARIMAX models and Poisson with covariates"),
                html.Li("For customer churn, we'll look at Cox proportional hazard, as well as adding \
                        covariates to our Weibull model"),
                html.Li("Customer segmentation, and unobserved heterogeneity")])
            ]),
        dbc.Col(),
    ], align='center'),]),
    dbc.Row([
        dbc.Col(width=1),
        dbc.Col()

    ], align='center'),])
