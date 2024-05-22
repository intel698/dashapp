import dash
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px
from dash import Input, Output, dcc, html

# Create a sample layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

# Sample function to create a figure
df = px.data.iris()

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                #dbc.NavLink("Page 1", href="/page-11", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
                dbc.NavLink("Page 3", href="/page-3", active="exact"),
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
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
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

# def draw_g(df):
#     graph1 = dcc.Graph(id='test1',
#                     figure=px.bar(df, x="sepal_width", y="sepal_length", color="species")
#                         .update_layout(
#                             template='plotly_dark',
#                             plot_bgcolor='rgba(0, 0, 0, 0)',
#                             paper_bgcolor='rgba(0, 0, 0, 0)',
#                         ),
#                     config={'displayModeBar': False}
#                 )
#     return graph1


app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(in_service),
            dbc.Col(html.Div("Text"), width=3),
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
@app.callback(Output("a0", "figure"),
              Input(in_service, 'value'))         
              #, [Input("url", "pathname")])
def update(option1):
    dff=df[df!=option1]

    fig=px.bar(dff, x="sepal_width", y="sepal_length", color="species")\
    .update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

                
    return fig



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
