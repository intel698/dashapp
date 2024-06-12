import dash
import dash_bootstrap_components as dbc
from dash import dcc, Dash, callback
import plotly.express as px
from dash import Input, Output, dcc, html

#! Not being used
dash.register_page(__name__, path='/KPI')

df = px.data.iris()
DARK_COLOR = 'rgba(0, 0, 0, 0)'

in_service =  dcc.RadioItems(
        id='option1',
        options=[
            {'label': 'setosa', 'value': 'setosa'},
            {'label': 'virginica', 'value': 'virginica'},
            {'label': 'versicolor', 'value': 'versicolor'}]
        , value='setosa' ) # Set the default value)

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

def actuals_container():
    return dbc.Container([
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
   
main_container = actuals_container()
layout = html.Div([main_container])


@callback([Output("a0", "figure")
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

