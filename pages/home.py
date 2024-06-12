import dash
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/home')

import requests
from PIL import Image
from io import BytesIO

card1 = dbc.Card(
    [
        dbc.CardImg(src="https://i.ibb.co/zQNMfDS/plan.png", top=True),
        dbc.CardBody(
            html.P("Subcription type business with three tier plans plus usage fees modeled as variable revenue"
                   , className="card-text")
        ),
    ],
    style={"width": "18rem"},
)

layout = html.Div([
dbc.Container([
    dbc.Row([
        dbc.Col(width=1),
        dbc.Col(children=[  

    html.H1("Machine Learning for Budgeting and Financial Forecasting"),
    html.P("This site is divided into three sections"),
    html.Ul([
        html.Li("Dashboard with traditional finance metrics (KPI)"),
        html.Li("Predicitve analytics for forecasting"),
        html.Li("Inference to understand customer behavior"),
    ]),
    html.P("For predictive analytics we will model 1) Customer additions, and 2) Customer churn \
           (survival) and 3) Variable Revenue to create a whole set of financial expectations:"),
    html.Ul([
        html.Li("For additions, we will use time series forecasting using a mix of modern \
                machine learning models as well as traditional ARIMA models"),
        html.Li("For customer churn, we will use maximum likelihood estimation and a Weibul distribution"),
    ]),
    #html.Br(),  
    html.P("For inference, we will look at the factors that influence customer behavior:"),
    html.Ul([
        html.Li("For additions we'll look at ARIMAX models and Poisson with covariates"),
        html.Li("For customer churn, we'll look at Cox proportional hazard, as well as adding \
                covariates to our Weibull model"),
        html.Li("Customer segmentation, and unobserved heterogeneity")
    ])

            ]),
    ], align='center'),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(card1), 
        dbc.Col()])
    
    ])])


# url = 'https://i.ibb.co/zfrQLyQ/image.png'
# response = requests.get(url)
# img = Image.open(BytesIO(response.content))


# card = dbc.Card(
#     [dbc.Row(
#             [dbc.Col(
#                 #html.Img(src='https://i.ibb.co/zfrQLyQ/image.png', style={'width': '50%', 'height': '50%'}),
#                 #dbc.CardImg(src="assets/image.png", top=True)
#                     ),
#             dbc.Col(
#                 dbc.CardBody(
#                     [html.H4("Overview", className="card-title"),
#                     html.P(
#                         "Our company follows a subscription business with three plans",
#                         className="card-text",
#                     ),
#                     html.Small(
#                         "Last updated 3 mins ago",
#                         className="card-text text-muted",
#                         ),
#                         ]
#                     ),
#                 ),
#             ],
#         )
#     ],
#     style={"maxWidth": "540px"},
# )