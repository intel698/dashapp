import dash
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px
from dash import Input, Output, dcc, html

# Create a sample layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

df = px.data.iris()
pathname = 'Actuals'

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

sidebar = html.Div(
    [
        html.H2(id="sidebar_title", className="display-4"),
        html.Hr(),
        html.H2(id='callback2', className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Actuals", href="/Actuals", active="exact"),
                dbc.NavLink("KPI", href="/KPI", active="exact"),
                dbc.NavLink("Predictive Analytics", href="/PredictiveAnalytics", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

def drawFigure(df, in_id):
    return html.Div([
        dbc.Card(dbc.CardBody([
            dcc.Graph(id = in_id,
                figure=px.bar(df, x="sepal_width", y="sepal_length", color="species")
                    .update_layout(
                        template='plotly_dark',
                        plot_bgcolor=DARK_COLOR,
                        paper_bgcolor=DARK_COLOR,
                    ),
                config={'displayModeBar': False}
            )
        ])),
    ])

in_service =  dcc.RadioItems(
        id='option1',
        options=[
            {'label': 'setosa', 'value': 'setosa'},
            {'label': 'virginica', 'value': 'virginica'},
            {'label': 'versicolor', 'value': 'versicolor'}], value='setosa' ) # Set the default value)


def actuals_container():
    return 1


main_container = actuals_container()

app.layout = html.Div([dcc.Location(id="url")
    , dbc.Container([sidebar])
    ,   dbc.Container([
        dbc.Row([
            dbc.Col(),
            dbc.Col(in_service),
            dbc.Col(html.Div("Text"), width=3),
            dbc.Col(html.Div("Text"), width=3),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(drawFigure(df, 'a0'), width=3),
            dbc.Col(drawFigure(df, 'a1'), width=3),
            dbc.Col(drawFigure(df, 'a2'), width=6),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(drawFigure(df, 'a3'), width=9),
            dbc.Col(drawFigure(df, 'a4'), width=3),
        ], align='center'),
    ])

])

@app.callback([Output("a0", "figure")
              ,Output("sidebar_title","children")]
              , [Input(in_service, 'value')
              , Input("url", "pathname")])         
def update_graph(option1, pathname):
    dff=df[df!=option1]

    fig=px.bar(dff, x="sepal_width", y="sepal_length", color="species")\
    .update_layout(
        template='plotly_dark',
        plot_bgcolor=DARK_COLOR,
        paper_bgcolor=DARK_COLOR,
    )
               
    return fig, pathname.replace("/", "")

# @app.callback([Output("callback2", "children")]   
#              , [Input("url", "pathname")])         
# def update_page(pathname):
#     return pathname.replace("/", "")


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
