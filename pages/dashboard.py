import dash
import dash_bootstrap_components as dbc
from dash import dcc, Dash, callback
import plotly.express as px
from dash import Input, Output, dcc, html
import os, sys

from pages.create_graphs import *
from pages.create_data import *
from pages.create_cards import *
from pages.create_table import *
import warnings
warnings.filterwarnings("ignore")

dash.register_page(__name__, path='/dashboard')

dfm, dfq, cust_detail = load()

#* Define variables
MY_STYLE = {'backgroundColor': '#495057', 'color': 'white'}
MY_CONFIG = {'displayModeBar': False}
per_currQ = pd.Period('2022Q4')
per_currM = per_currQ.asfreq('M')
per_list = get_period_list(per_currQ, 6)


#*# Create result graphs
# Main graphs
df1 = dfq[dfq.index.isin(per_list)]
dccg1 = dcc.Graph(figure = create_results_graph(df1, 'Revenue')
                  , config = MY_CONFIG
                  , style={ 'height': '40vh'})

#Waterfall Revenue Walk
df22 = list(data_compare_periods(dfq, per_currQ, 4).values())
dccg22 = dcc.Graph(figure = create_compare_graph(df22)
                  , config = MY_CONFIG
                  , style={'height': '40vh'})

# Breakout by plan
df3 = pivot_data_by_quarter(dfq)
dccg3 = dcc.Graph(figure = create_byplan_graph(df3.loc[df3.index<per_currQ,:])
                  , config = MY_CONFIG
                  , style={'height': '40vh'})
#

def create_result_table(dfq, per_currQ):
    dfq = get_table_data(dfq, per_currQ)
    result_table = dash_table_object('result_table')
    result_table.style_cell = {'textAlign': 'center', 'width': '30px', 'backgroundColor': '#272b30', 'color': 'white'}
    result_table.style_cell_conditional = [
                {'if': {'column_id': '($ in thousands)'},  
                'textAlign': 'left',
                'minWidth': '50px',
                'width': '50px',
                'maxWidth': '50px',
                'height': 'auto',
                'whiteSpace': 'normal',
                }]

    base_dict =  {'if': {'row_index': 0},  
                'backgroundColor': '#272b30',
                'color': 'white',
                'fontSize': '12px'}

    result_table.style_data_conditional= [{**base_dict, 'if': {'row_index': row}} for row in [1, 2, 4, 5]]
    result_table = result_table.create_table(dfq)
    return create_card_graph(result_table)




card0 = create_card_factory('card', 'Active Users', 10.2, 'Up 10% YoY')
card1 = create_card_factory('card1', 'Revenue per user', 10.2, 'Up 10% YoY')
card2 = create_card_factory('card2', 'Retention rate', '70%', 'Flat YoY')
card3 = create_card_factory('card3', 'Median tenure', '27 months', 'Flat but great')
card4 = create_card_factory('card4', 'Booking Backlog', '$315M', 'Increasing')
card5 = create_card_factory('card00', 'Period Revenue', 10.2, 'Up 10% YoY')

result_table = create_result_table(dfq, per_currQ)
card_table1 = html.Div(children=[result_table])

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
    style=MY_STYLE|{'width': '100px'})

dcc_qtr = dcc.Dropdown(
    options=[
        {'label': 'Q1', 'value': "Q1"},
        {'label': 'Q2', 'value': "Q2"},
        {'label': 'Q3', 'value': "Q3"},
        {'label': 'Q4', 'value': "Q4"},
    ],
    clearable=False,
    value="Q4",
    style=MY_STYLE|{'width': '100px'})

dcc_cc = dcc.Checklist(
    ['Constant Currency'],
    id='my-checkbox',
    labelStyle={'display': 'block'}, 
    style=MY_STYLE)
    

layout = html.Div([
dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card(children = [
                    html.Label('Select a Year:'), dcc_year,
                    html.Label('Select a Qtr:'), dcc_qtr,
                    dcc_cc]), width=2),
            dbc.Col(card5.card, width=2),
            dbc.Col(card0.card, width=2),
            dbc.Col(card1.card, width=2),
            dbc.Col(card2.card, width=2),
            dbc.Col(card3.card, width =2),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(create_card_graph(dccg1), width=5),
            dbc.Col(create_card_graph(dccg22), width=7), 
            #dbc.Col(dccg2, width=4),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col(card_table1, width=6),
            dbc.Col(create_card_graph(dccg3), width=6),
        ], align='center'),
        html.Br(),
    ]),
])


@callback(
    [Output(dccg1, 'figure'),
     Output(dccg22, 'figure'),
     Output(dccg3, 'figure'),
     Output(card_table1, 'children'),
     Output(card0.text_id, 'children'),
     Output(card0.para_id, 'children'),
     Output(card1.text_id, 'children'), 
     Output(card1.para_id, 'children'),                     
     Output(card2.text_id, 'children'),
     Output(card3.text_id, 'children'),  
     Output(card5.text_id, 'children'),
     Output(card5.para_id, 'children')
    ],
    [Input(dcc_qtr, 'value'), 
     Input(dcc_year, 'value')]
)
def drop_down_changed(qtr, yr):
    per_currQ = pd.Period(str(yr) + qtr)
    per_currM = per_currQ.asfreq('M')
    per_list_g11 = get_period_list(per_currQ, 6)


    df1 = dfq[dfq.index.isin(per_list_g11)]   
    df2 = list(data_compare_periods(dfq, per_currQ, 4).values())

    revenue = dfq.loc[dfq.index==per_currQ, 'Revenue'].values[0]/1000
    revenue_yoy = pct(dfq.loc[dfq.index==per_currQ, 'Revenue'].values[0]
                    , dfq.loc[dfq.index==(per_currQ-4), 'Revenue'].values[0])
    arpu = dfq.loc[dfq.index==per_currQ, 'ARPU'].values[0]
    arpu_yoy = pct(dfq.loc[dfq.index==per_currQ, 'ARPU'].values[0]
                , dfq.loc[dfq.index==(per_currQ-4), 'ARPU'].values[0])
    cust_count = dfq.loc[dfq.index==per_currQ, 'End_Count'].values[0]
    cust_count_yoy = pct(dfq.loc[dfq.index==per_currQ, 'End_Count'].values[0],
                    dfq.loc[dfq.index==(per_currQ-4), 'End_Count'].values[0]) 
                         
    retention = "{:,.1%}".format(dfq.loc[dfq.index==per_currQ, 'Retention'].values[0])  
    median_life = str(calculate_median_duration(cust_detail, per_currM))+ " months"

    
    return [ create_results_graph(df1 , 'Revenue')
            , create_compare_graph(df2)
            , create_byplan_graph(df3.loc[df3.index<=per_currQ,:])
            , create_result_table(dfq, per_currQ)
            , f"{cust_count:,}"
            , cust_count_yoy + " YoY"
            , f"${arpu:,.1f}"
            , arpu_yoy+ " YoY"
            , retention
            , median_life
            , f"${revenue:,.1f}"
            , revenue_yoy + " YoY"
            ] 
            

