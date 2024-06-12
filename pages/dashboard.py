import dash
import dash_bootstrap_components as dbc
from dash import dcc, Dash, callback
import plotly.express as px
from dash import Input, Output, dcc, html


from pages.create_graphs import *
from pages.create_data import *
from pages.create_cards import *

dash.register_page(__name__, path='/dashboard')

df, dfq, cust_detail = load()

#* Define variables

DARK_COLOR = 'rgba(0, 0, 0, 0)'
MY_STYLE = {'backgroundColor': 'rgba(207, 207, 207, 207)', 'color': 'black'}

id_counter = 0
id_card_list = []

per_currQ = pd.Period('2022Q4')
per_currM = per_currQ.asfreq('M')
per_month_strftime_Mmm = per_currM.to_timestamp().strftime('%b')

per_list_g1 = period_list(per_currQ, 6)
per_list_g2 = period_list(per_currQ, 5)

#*# Create result graphs
# Main graphs
df1 = dfq[dfq.index.isin(per_list_g1)]
g1 = create_results_graph(df1, 'Revenue')
dccg1 = dcc.Graph(figure=g1, config={'displayModeBar': False}, style={ 'height': '40vh'})

#Waterfall Revenue Walk
df4 = data_compare_periods(dfq, per_currQ, per_currQ-4)
lay4 = create_layout("Revenue Walk YoY", "Change in revenue by category", "Change in $",legend= False)
g4 = create_compare_graph(lay4, df4)
dccg4 = dcc.Graph(figure = g4, id = 'g4', config={'displayModeBar': False}, style={'height': '40vh'})

# Breakout by plan
df2 = data_transform_plan_df(cust_detail, dfq)
g2 = create_byplan_graph(df2.loc[df2.index<per_currQ,:])
dccg2 = dcc.Graph(figure = g2, id='g2',  config={'displayModeBar': False}, style={'height': '40vh'})

# Customer detail by plan by household
df3 = cust_detail[cust_detail[per_currQ]!=0]\
            .groupby(['plan', 'household','duration'])[per_currQ].count().reset_index()
g3 = create_customer_profile_graph(df3)
dccg3 = dcc.Graph(figure = g3, id='g3',  config={'displayModeBar': False}, style={'height': '40vh'})


#Customer additions per month
lay5 = create_layout("Customer additions per month", "Months", "Number of customers", legend = False)
g5 = create_month_add_graph(lay5, df, per_currM.to_timestamp().strftime('%b'), df.at[per_currM, 'Net_add'])
dccg5 = dcc.Graph(figure = g5, id = 'g5',  config={'displayModeBar': False}, style={'height': '40vh'})


top_cards = create_object()

card1 = top_cards.create_card("Total ARPU", 10.2, "Up 10% YoY")
card2 = top_cards.create_card("Retention rate", "70%", "Flat YoY")
card3 = top_cards.create_card("Median tenure", "27 months", "Flat but great")
card4 = top_cards.create_card("Booking Backlog", "$315M", "Increasing")

# * Create inputs
dcc_year = dcc.Dropdown(
    options=[
        {'label': '2019', 'value': 2019},
        {'label': '2020', 'value': 2020},
        {'label': '2021', 'value': 2021},
        {'label': '2022', 'value': 2022},
    ],
    clearable=False,
    value=2022,
    style=MY_STYLE)

dcc_qtr = dcc.Dropdown(
    options=[
        {'label': 'Q1', 'value': "Q1"},
        {'label': 'Q2', 'value': "Q2"},
        {'label': 'Q3', 'value': "Q3"},
        {'label': 'Q4', 'value': "Q4"},
    ],
    clearable=False,
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
            dbc.Col(create_card_graph(dccg1), width=5),
            dbc.Col(create_card_graph(dccg4), width=7), 
            #dbc.Col(dccg2, width=4),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(create_card_graph(dccg3), width=7),
            dbc.Col(create_card_graph(dccg2), width=5),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(create_card_graph(dccg5), width=9),
        ], align='center'),
    ]),
])


@callback(
    [Output(dccg1, 'figure'),
     Output(dccg4, 'figure'),
     Output(dccg5, 'figure'),
     Output(dccg3, 'figure'),
     Output(dccg2, 'figure'),
     Output(top_cards.id_card_list[0][0], 'children'), 
     Output(top_cards.id_card_list[0][1], 'children'),                     
     Output(top_cards.id_card_list[1][0], 'children'),
     Output(top_cards.id_card_list[2][0], 'children'),                             
                            ],
    [Input(dcc_qtr, 'value'), 
     Input(dcc_year, 'value')]
)
def drop_down_changed(qtr, yr):
    per_currQ = pd.Period(str(yr)+qtr)
    per_currM = per_currQ.asfreq('M')
    per_list_g11 = period_list(per_currQ, 6)
    per_month_strftime_Mmm = per_currM.to_timestamp().strftime('%b')

    df1 = dfq[dfq.index.isin(per_list_g11)]
    

    df3 = cust_detail[cust_detail[per_currQ]!=0]\
            .groupby(['plan', 'household','duration'])[per_currQ].count().reset_index()
    
    df4 = data_compare_periods(dfq, per_currQ, per_currQ-4)

    ARPU = "${:,.1f}".format(dfq.loc[dfq.index==per_currQ, 'ARPU'].values[0])
    ARPU_YOY = pct(dfq.loc[dfq.index==per_currQ, 'ARPU'].values[0]
                , dfq.loc[dfq.index==(per_currQ-4), 'ARPU'].values[0]) + " YoY"
    RETENTION = "{:,.1%}".format(dfq.loc[dfq.index==per_currQ, 'Retention'].values[0])
    
    df5, _ = data_create_avg_life_df(cust_detail)
    MEDIAN_LIFE = calculate_median_duration(df5, per_currM)

    
    return [ create_results_graph(df1 , 'Revenue')
            , create_compare_graph(lay4, df4)
            , create_month_add_graph(lay5, df 
                    , per_month_strftime_Mmm
                    , df.at[per_currM, 'Net_add'])
            , create_customer_profile_graph(df3)
            , create_byplan_graph(df2.loc[df2.index<=per_currQ,:])
            , ARPU
            , ARPU_YOY
            , RETENTION
            , MEDIAN_LIFE
            ] 
            

