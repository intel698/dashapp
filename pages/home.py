import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/')

linkgroup =    html.Div(
    children=[
        html.A(
            href="https://www.linkedin.com/in/ruben-giro/", 
            children=[
                html.Img(
                    src="https://i.ibb.co/M92Jn6Q/linked.png",  
                    style={"width": "50px", "height": "50px", 'vertical-align': 'bottom'}  
                ), 
                html.H6("About me")
            ],
            style={'display':'inline-block', 'vertical-align': 'bottom', 'margin-right': '20px', 'position': 'absolute', 'bottom': '0'}
        ),
        html.A(
            href="https://github.com/intel698/dashapp/tree/main",
            children=[
                html.Img(
                    src="https://i.ibb.co/wQXw08x/Git-Hub-Logo-White.png",  
                    style={"width": "100px", "height": "25px", 'vertical-align': 'bottom'}  
                ), 
                html.H6("Source")
            ],
            style={'display':'inline-block', 'vertical-align': 'bottom', 'position': 'absolute', 'bottom': '0'}
        ),
    ],
    style={'display': 'flex', 'align-items': 'bottom'}
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

    linkgroup 
    ])


])

