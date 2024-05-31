import dash
import dash_bootstrap_components as dbc
from dash import dcc, Dash, callback
import plotly.express as px
from dash import Input, Output, dcc, html
from graph import *

dash.register_page(__name__, path='/PredictiveAnalytics')
DARK_COLOR = 'rgba(0, 0, 0, 0)'
id_counter = 0

per_currQ = pd.Period('2022Q4')
per_currM = pd.Period('2022-12')
per_list_g1 = period_list(per_currQ, 8)
per_list_g2 = period_list(per_currQ, 5)

df1 = dfq[dfq.index.isin(per_list_g1)]
g1 = create_results_graph(df1, 'Revenue').show()
g11 = create_results_graph(df1, 'End_Count').show()

g2 = cust_detail.groupby('hotspot')[per_list_g2].sum()
create_byplan_graph(g2).show()

g3 = cust_detail[cust_detail[per_currQ]!=0].groupby(['hotspot'
        , 'Household','duration'])[per_currQ].count().reset_index()
create_customer_profile_graph(g3).show()

g4 = compare_periods(dfq, per_currQ, per_currQ-4)
create_compare_graph(g4).show()

g5 = df
create_month_add_graph(g5, 'Jun', 1200).show()


dcc_g1 = dcc.Graph(figure=g1, id='g1')
dcc_g11 = dcc.Graph(figure=g11, id='g11')

def create_card(header="Marketing", text ="Main text", para = "bottomtext"):
    header_id = "id" + str(id_counter)
    text_id = "id" + str(id_counter)
    para_id = "id" + str(id_counter)
    id_counter +=1

    card1 = dbc.Card(
        [
            dbc.CardHeader(header),
            dbc.CardBody(
                [
                    html.H4(id=text_id, className="card-title"),
                    html.P(id=para_id,className="card-text"),
                ]
            ),
        ],)
        #style={"width": "30rem"},)
    return card1


layout = html.Div([
dbc.Container([
        dbc.Row([
            dbc.Col(create_card()),
            dbc.Col(create_card()),
            dbc.Col(create_card(), width=3),
            dbc.Col(create_card(), width=3),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc_g1, width=6),
            dbc.Col(dcc_g11, width=6),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Div("Text"), width=9),
            dbc.Col(html.Div("Text"), width=3),
        ], align='center'),
    ])
])

# @callback([Output("a0", "figure")
#               , Input("url", "pathname")])         
# def update_graph(option1, pathname):
#     dff=df[df!=option1]

#     fig=px.bar(dff, x="sepal_width", y="sepal_length", color="species")\
#     .update_layout(
#         template='plotly_dark',
#         plot_bgcolor=DARK_COLOR,
#         paper_bgcolor=DARK_COLOR,
#     )
               
#     return fig, pathname.replace("/", "")

