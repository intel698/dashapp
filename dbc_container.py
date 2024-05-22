import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

# Create a sample layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

# Sample function to create a figure
def drawFigure():
    df = px.data.iris()
    return html.Div([
        dbc.Card(dbc.CardBody([
            dcc.Graph(
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

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div("Text"), width=3),
            dbc.Col(html.Div("Text"), width=3),
            dbc.Col(html.Div("Text"), width=3),
            dbc.Col(html.Div("Text"), width=3),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(drawFigure(), width=3),
            dbc.Col(drawFigure(), width=3),
            dbc.Col(drawFigure(), width=6),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(drawFigure(), width=9),
            dbc.Col(drawFigure(), width=3),
        ], align='center'),
    ])
])



# Run the app
if __name__ == '__main__':
    app.run_server()
