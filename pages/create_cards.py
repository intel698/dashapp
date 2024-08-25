import dash
import dash_bootstrap_components as dbc
from dash import html
from dash import Input, Output, dcc, html

DARK_COLOR = 'rgba(0, 0, 0, 0)'
MY_STYLE = {'backgroundColor': 'rgba(207, 207, 207, 207)', 'color': 'black'}

# Iteratively create cards with ids:
# text_id(n) - to access header
# para_id(n) - to access main text
class create_card_factory:
    def __init__(self, id_to_use, header, init_text, init_para):
        self.id_to_use = id_to_use     
        self.text_id = "text_id" + id_to_use
        self.para_id = "para_id" + id_to_use
        self.header = header

        self.card = dbc.Card(
            [
                dbc.CardHeader(header),
                dbc.CardBody(
                    [
                        html.H4(init_text, id=self.text_id, className="card-title"),
                        html.P(init_para, id=self.para_id, className="card-text"),
                    ]),
            ]) 
#* Takes a graph and puts it inside a card
def create_card_graph(graph_in):
    card = dbc.Card([dbc.CardBody([graph_in])]) 
    return card 
