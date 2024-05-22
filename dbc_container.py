import dash
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.express as px
from dash import Input, Output, dcc, html

# Create a sample layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

# Sample function to create a figure
df = px.data.iris()

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
