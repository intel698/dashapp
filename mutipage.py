import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px

df = px.data.iris()
fig = px.bar(df, x="sepal_width", y="sepal_length", color="species", title=" initial title")

# df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
# fig = px.scatter(x=df['Year'],
#                  y=df['Value'])

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
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
#  children= [dcc.Graph(id='ig')]

#content = html.Div(id="page-content", style=CONTENT_STYLE)

content= html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Camaguey"), width=3),
            dbc.Col(html.H2("Text2"), width=3),
            dbc.Col(html.H2("Text3"), width=3),

        ], align='right'),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Graph(id='test1'))
        ])])])

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("test1", "figure")
              , [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        fig.update_layout(title=dict(text="Home0", font=dict(size=22)
                                     , automargin=True))
        print('h1')
        return fig #html.P("This is the content of the home page!")
    # elif pathname == "/page-11":
    #     fig.update_layout(title=dict(text="Page111", font=dict(size=22)
    #                             , automargin=True))
    #    print('h2')
    #    return fig, #html.P("This is the content of page 1. Yay!")
    elif pathname == "/page-2":
        fig.update_layout(title=dict(text="Page22", font=dict(size=22)
                                , automargin=True))
        print('h3')
        return fig #html.P("Oh cool, this is page 2!")
    elif pathname == "/page-3":
        fig.update_layout(title=dict(text="Page33", font=dict(size=22)
                                , automargin=True))
        print('h4')
        return fig #html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    # return html.Div(
    #     [
    #         html.H1("404: Not found", className="text-danger"),
    #         html.Hr(),
    #         html.P(f"The pathname {pathname} was not recognised..."),
    #     ],
    #     className="p-3 bg-light rounded-3",
    # )


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)