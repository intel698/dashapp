import pandas as pd
# from create_data import *
# from create_graphs import *
from pages.create_data import *
from dash import Input, Output, dcc, html

# df, dfq, cust_detail = load()

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# Generate some example data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Define the layout of the app
app.layout = html.Div([
    dcc.Slider(
        id='slider',
        min=0,
        max=10,
        step=0.1,
        value=5,
        marks={i: str(i) for i in range(11)},
    ),
    dcc.Graph(id='graph')
])

# Define the callback to update the graph based on the slider value
@app.callback(
    Output('graph', 'figure'),
    Input('slider', 'value')
)
def update_graph(slider_value):
    # Generate new data based on the slider value
    y_new = np.sin(x + slider_value)
    
    # Create the figure
    fig = go.Figure(data=[
        go.Scatter(x=x, y=y_new, mode='lines')
    ])
    
    fig.update_layout(
        title=f'Sine Wave with Phase Shift of {slider_value}',
        xaxis_title='X Axis',
        yaxis_title='Y Axis'
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
