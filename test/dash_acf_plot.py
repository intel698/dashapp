# File path: app.py

# fig, ax = plt.subplots()

# fig0 = sm.graphics.tsa.plot_acf(df['Adds'], lags=30)
# plot_acf(df['Adds'], lags=30, ax=ax)
# plotly_fig = tls.mpl_to_plotly(fig)

# Step 1: Import Libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from statsmodels.tsa.stattools import acf

# Step 2: Load Data
# For simplicity, we'll generate a sample time series data
data = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0])

# Step 3: Compute Auto-Correlation
autocorr_values, confint = acf(data, nlags=20, alpha=0.05)

# Calculate the upper and lower bounds of the confidence intervals
confint_lower = confint[:, 0] - autocorr_values
confint_upper = confint[:, 1] - autocorr_values

# Step 4: Create Plot
autocorr_plot = go.Figure()

# Add auto-correlation values as a bar chart
autocorr_plot.add_trace(go.Bar(
    x=list(range(len(autocorr_values))),
    y=autocorr_values,
    name='Auto-Correlation'
))

# Add confidence intervals as filled areas
autocorr_plot.add_trace(go.Scatter(
    x=list(range(len(autocorr_values))),
    y=confint_upper,
    mode='lines',
    line=dict(color='blue'),
    name='Upper Confidence Bound',
    showlegend=False
))

autocorr_plot.add_trace(go.Scatter(
    x=list(range(len(autocorr_values))),
    y=confint_lower,
    mode='lines',
    fill='tonexty',
    line=dict(color='blue'),
    name='Lower Confidence Bound',
    showlegend=False
))

# Add horizontal lines for significance thresholds
threshold_upper = 1.96 / (len(data) ** 0.5)
threshold_lower = -1.96 / (len(data) ** 0.5)

autocorr_plot.add_shape(type="line", x0=0, x1=len(autocorr_values)-1, y0=threshold_upper, y1=threshold_upper,
                        line=dict(color="red", dash="dash"))
autocorr_plot.add_shape(type="line", x0=0, x1=len(autocorr_values)-1, y0=threshold_lower, y1=threshold_lower,
                        line=dict(color="red", dash="dash"))

autocorr_plot.update_layout(
    title='Auto-Correlation Plot with Confidence Bands',
    xaxis_title='Lags',
    yaxis_title='Auto-Correlation'
)

# Step 5: Setup Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Auto-Correlation Plot"),
    dcc.Graph(id='autocorr-graph', figure=autocorr_plot)
])

if __name__ == '__main__':
    app.run_server(debug=True)
