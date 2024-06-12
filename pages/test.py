import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.tools as tls
import numpy as np
from create_data import load
import dash
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output


df, dfq, cust_detail = load()
df = df.loc[df.index <= pd.Period('2022-12', 'M'), :]
graph_df = df.copy()
graph_df.set_index(graph_df.index.astype(str), inplace=True)
# Step 1: Load Data

# Step 2: Decompose Time Series
result = seasonal_decompose(graph_df['Adds'], model='additive', period=12)

# Step 3: Create Dash App
app = Dash(__name__)

# Create Figures
original_fig = go.Figure()
original_fig.add_trace(go.Scatter(x=graph_df.index, y=df['Drops'], mode='lines', name='Original'))


trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend, mode='lines', name='Trend'))

seasonal_fig = go.Figure()
seasonal_fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, mode='lines', name='Seasonal'))

residual_fig = go.Figure()
residual_fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid, mode='lines', name='Residual'))

trend_fig.show()

