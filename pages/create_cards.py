import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import Input, Output, dcc, html

DARK_COLOR = 'rgba(0, 0, 0, 0)'
MY_STYLE = {'backgroundColor': 'rgba(207, 207, 207, 207)', 'color': 'black'}

class create_object:
    def __init__(self):
      self.id_counter = 0
      self.id_card_list = []
      

    # * Create cards
    def create_card(self, header, init_text, init_para):
        text_id = "text_id" + str(self.id_counter)
        para_id = "para_id" + str(self.id_counter)

        self.id_counter +=1     
        self.id_card_list.append((text_id, para_id))

        card = dbc.Card(
            [
                dbc.CardHeader(header),
                dbc.CardBody(
                    [
                        html.H4(init_text, id=text_id, className="card-title"),
                        html.P(init_para, id=para_id, className="card-text"),
                    ]),
            ],) #style={"width": "30rem"},)
        return card 
    

#* Create graph cards
def create_card_graph(graph_in):
    card = dbc.Card([dbc.CardBody([graph_in])]) #style={"width": "30rem"},)
    return card 

dcc_qtr1 = dcc.Dropdown(
options=[
    {'label': 'Q1', 'value': "Q1"},
    {'label': 'Q2', 'value': "Q2"},
    {'label': 'Q3', 'value': "Q3"},
    {'label': 'Q4', 'value': "Q4"},
],
value="Q4",
style= {'backgroundColor': 'rgba(207, 207, 207, 207)'
        , 'color': 'black'
        , 'width': '30rem'
        }

)

def create_card_graph_option(graph_in):
    card = dbc.Card([dbc.CardBody([dcc_qtr1, graph_in])]) #style={"width": "30rem"},)
    return card 