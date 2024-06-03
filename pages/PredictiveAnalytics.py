import dash
import dash_bootstrap_components as dbc
from dash import dcc, Dash, callback
import plotly.express as px
from dash import Input, Output, dcc, html
from pages.graph import *
from pages.load_data import *

dash.register_page(__name__, path='/PredictiveAnalytics')

DARK_COLOR = 'rgba(0, 0, 0, 0)'
MY_STYLE = {'backgroundColor': 'rgba(207, 207, 207, 207)', 'color': 'black'}

id_counter = 0
id_card_list = []

per_currQ = pd.Period('2022Q4')
per_currM = per_currQ.asfreq('M')

per_list_g1 = period_list(per_currQ, 6)
per_list_g2 = period_list(per_currQ, 5)

#*# Create graphs
# Main graphs
df1 = dfq[dfq.index.isin(per_list_g1)]
g1 = create_results_graph(df1, 'Revenue')
dccg1 = dcc.Graph(figure=g1)

#Waterfall Revenue Walk
df4 = compare_periods(dfq, per_currQ, per_currQ-4)
lay4 = create_layout("Revenue Walk YoY", "Change in revenue by category", "Change in $",legend= False)
g4 = create_compare_graph(lay4, df4)
dccg4 = dcc.Graph(figure = g4, id = 'g4')

# Breakout by plan
df2 = cust_detail.groupby('plan')[per_list_g2].sum()
lay2 = create_layout("Revenue Breakout by Plan")
g2 = create_byplan_graph(lay2, df2)
dccg2 = dcc.Graph(figure = g2, id='g2')

# Customer detail by plan by household
df3 = cust_detail[cust_detail[per_currQ]!=0]\
            .groupby(['plan', 'household','duration'])[per_currQ].count().reset_index()
g3 = create_customer_profile_graph(df3)
#g3 = set_layout_axis_one(g3, "Customer Profile")
dccg3 = dcc.Graph(figure = g3, id='g3')


#Customer additions per month
lay5 = create_layout("Customer additions per month", legend = False)
g5 = create_month_add_graph(lay5, df, per_currM.to_timestamp().strftime('%b'), df.at[per_currM, 'Net_add'])
dccg5 = dcc.Graph(figure = g5, id = 'g5')


# * Create cards
def create_card(header, init_text, init_para):
    global id_counter
    #header_id = "id" + str(id_counter)
    text_store_id = "store_id" + str(id_counter)
    para_store_id = "store_id" + str(id_counter)
    text_id = "text_id" + str(id_counter)
    para_id = "para_id" + str(id_counter)

    id_counter +=1
    id_card_list.append((text_id, para_id))

    # Create initial value
    store_init_text = dcc.Store(id = text_store_id, data=init_text)
    store_init_para = dcc.Store(id = para_store_id, data=init_para)

    # Create card
    card = dbc.Card(
        [
            dbc.CardHeader(header),
            dbc.CardBody(
                [
                    html.H4(init_text, id=text_id, className="card-title"),
                    html.P(init_para, id=para_id, className="card-text"),
                ]
            ),
        ],) #style={"width": "30rem"},)

    return card #, store_init_text, store_init_para

ARPU = 10.2
RETENTION = '70%'
TENURE = "27 months"
BACKLOG = "$315M"
card1 = create_card("Total ARPU", ARPU, "Up 10% YoY")
card2 = create_card("Retention rate", RETENTION, "Flat YoY")
card3 = create_card("Median tenure", TENURE, "Flat but great")
card4 = create_card("Booking Backlog", BACKLOG, "Increasing")

# * Create inputs
dcc_year = dcc.Dropdown(
    options=[
        {'label': '2019', 'value': 2019},
        {'label': '2020', 'value': 2020},
        {'label': '2021', 'value': 2021},
        {'label': '2022', 'value': 2022},
    ],
    value=2022,
    style=MY_STYLE)

dcc_qtr = dcc.Dropdown(
    options=[
        {'label': 'Q1', 'value': "Q1"},
        {'label': 'Q2', 'value': "Q2"},
        {'label': 'Q3', 'value': "Q3"},
        {'label': 'Q4', 'value': "Q4"},
    ],
    value="Q4",
    style=MY_STYLE)

dcc_cc = dcc.Checklist(
    ['Constant Currency'],
    id='my-checkbox',
    labelStyle={'display': 'block'}, 
    style={'backgroundColor':DARK_COLOR})
    

layout = html.Div([
dbc.Container([
        dbc.Row([
            dbc.Col(width=2),
            dbc.Col(children = [html.Label('Select a Year:'), dcc_year,
                                html.Label('Select a Qtr:'), dcc_qtr,
                                dcc_cc], width=2),
            dbc.Col(card1, width=2),
            dbc.Col(card2, width=2),
            dbc.Col(card3, width=2),
            dbc.Col(card4, width =2),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(dccg1, width=5),
            dbc.Col(dccg4, width=7), 
            #dbc.Col(dccg2, width=4),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(dccg3, width=7),
            dbc.Col(dccg2, width=5),
        ], align='center'),
        dbc.Row([
            dbc.Col(dccg5, width=9),
        ], align='center'),
    ])
])

#id_card_list.append((text_id, para_id))

@callback(
    [Output(dccg1, 'figure'),
     Output(dccg4, 'figure'),
     Output(dccg5, 'figure'),
     Output(dccg3, 'figure'),
     Output(id_card_list[0][0], 'children'), 
     Output(id_card_list[0][1], 'children'),                     
     Output(id_card_list[1][0], 'children'),                            
                                            ],
    [Input(dcc_qtr, 'value'), 
     Input(dcc_year, 'value')]
)
def drop_down_changed(qtr, yr):
    per_currQ = pd.Period(str(yr)+qtr)
    per_currM = per_currQ.asfreq('M')
    per_list_g1 = period_list(per_currQ, 6)

    df1 = dfq[dfq.index.isin(per_list_g1)]
    df3 = cust_detail[cust_detail[per_currQ]!=0]\
            .groupby(['plan', 'household','duration'])[per_currQ].count().reset_index()
    df4 = compare_periods(dfq, per_currQ, per_currQ-4)

    ARPU_yoy = pct(dfq.loc[dfq.index==per_currQ, 'ARPU'].values[0]
                , dfq.loc[dfq.index==(per_currQ-4), 'ARPU'].values[0]) + " YoY"


    return [ create_results_graph(df1 , 'Revenue')
            , create_compare_graph(lay4, df4)
            , create_month_add_graph(lay5, df 
                , per_currM.to_timestamp().strftime('%b')
                , df.at[per_currM, 'Net_add'])
            , create_customer_profile_graph(df3)
            , "${:,.1f}".format(dfq.loc[dfq.index==per_currQ, 'ARPU'].values[0])
            , ARPU_yoy
            , "{:,.1%}".format(dfq.loc[dfq.index==per_currQ, 'Retention'].values[0])
            ] 
            

