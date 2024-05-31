import dash
import dash_bootstrap_components as dbc
from dash import dcc, Dash
import plotly.express as px
from dash import Input, Output, html
import os

pages_folder=os.path.join(os.path.dirname(__name__), "pages")

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SLATE])

app.config['suppress_callback_exceptions'] = True


DARK_COLOR = 'rgba(0, 0, 0, 0)'
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "2rem 1rem",
    "background-color": 'rgba(0, 0, 0, 0)',
}
df = px.data.iris()
sidebar = html.Div(
    [
        html.H2(id="sidebar_title", className="display-4"),
        html.Hr(),
        html.H2(id='callback2', className="lead"),
        dbc.Nav(
            [
            dbc.NavLink("Home", href="/home", active="exact"),
            dbc.NavLink("Dashboard", href="/KPI", active="exact"),   
            dbc.NavLink("Predictive Analytics", href="/PredictiveAnalytics", active="exact"),
            dbc.NavLink("Inference", href="/Actuals", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE
)

app.layout = html.Div([dcc.Location(id="url")
    , dbc.Container([sidebar]),
    dash.page_container
])

if __name__ == '__main__':
    print(__file__)
    app.run(debug=False)
