import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import dash_bootstrap_components as dbc
try:from create_data import *
except:from pages.create_data import *

DARK_COLOR = 'rgba(0, 0, 0, 0)'

#*## Create graph layouts
def create_layout(mtitle = "Title goes here", xtitle="X title", ytitle ="y title", legend = True):
    return go.Layout(
        plot_bgcolor=DARK_COLOR,
        paper_bgcolor=DARK_COLOR,
        template='plotly_dark',
        title=dict(
            text=mtitle,
            font=dict(size=14),
            x=0.5,  # Center the title horizontally
            xanchor='center'),
        xaxis=dict(tickfont=dict(size=12), title=xtitle),
        yaxis=dict(tickfont=dict(size=12), title=ytitle),
        showlegend=legend,
        margin=dict(l=10, r=10, t=20, b=10),
        )

def dark_layout(fig, main_title = None):
    fig.update_layout(
    plot_bgcolor=DARK_COLOR,
    paper_bgcolor=DARK_COLOR,
    template='plotly_dark',
    title=dict(
        text=main_title,
        font=dict(size=14),
        x=0.5,  # Center the title horizontally
        xanchor='center'),
    margin=dict(l=10, r=10, t=20, b=10)
    )
    return fig

#*### Create graphs ****
#* Actual results graph
def create_results_graph(dfqq, columna):
    
    dfqq.index =  [str(i)[:4] + str(i)[-2:] for i in dfqq.index]
    #log_variable("enter create graph func", columna, dfqq.shape)

    fig0 = go.Figure(layout=go.Layout(
        plot_bgcolor=DARK_COLOR,
        paper_bgcolor=DARK_COLOR,
        template='plotly_dark',
        title=dict(
            text="Quarterly Revenue",
            font=dict(size=16),
            x=0.5,  # Center the title horizontally
            xanchor='center'),
        xaxis=dict(tickfont=dict(size=12), title="Quarters"),
        yaxis=dict(tickfont=dict(size=12), title="Revenue (M)"),
        margin=dict(l=10, r=10, t=20, b=10),

        yaxis2=dict(title="Change (%)", overlaying='y', side='right' ,tickformat=',.0%'),  
        showlegend=True,
        legend=dict(
            orientation='h',
            x=0,  
            y=1.1 )    
  ))

    fig0.update_traces(texttemplate='%{y:$,.0f}', textfont=dict(size=26))
    fig0.add_shape(type="line", x0=0, x1=1, xref="paper", y0=0, y1=0, yref="y2", line=dict(color="Red", width=2,dash="dashdot"))

    
    fig0.add_trace(go.Bar(x=dfqq.index, y=dfqq[columna], name="Revenue"))
    fig0.add_trace(go.Scatter(x=dfqq.index, y=dfqq[columna+"_PoP"], mode='lines', line=dict(width=5),name='% chg QoQ', yaxis='y2'))  # Specify secondary y-axis
    fig0.add_trace(go.Scatter(x=dfqq.index, y=dfqq[columna+"_YoY"], mode='lines', line=dict(width=5),name='% chg YoY', yaxis='y2'))  # Specify secondary y-axis

    return fig0
#*# Waterfall chart to compare period over period
def create_compare_graph(delta_nn_per):
    list_waterfall = ['Basic', 'Standard', 'Premium', 'Basic Plan'
                      , 'Std Plan', 'Prem Plan', 'Var Revenue']
    fig3 = go.Figure(layout= create_layout("Revenue Walk YoY"
                                           , "Change in revenue by category"
                                           , "Change in $", legend= False)
                     )
    fig3.add_trace(go.Waterfall(
        name = "2024",
        orientation = "v",
        measure = ['relative'] * 7,
        x = [['--Customer Additions--', '--Customer Additions--'
              ,'--Customer Additions--', '-----Change in price-----'
              ,'-----Change in price-----','-----Change in price-----','--Other--']
              , list_waterfall],
        y = delta_nn_per,
        textposition = "outside",
        text = [f'{int(y):,}' for y in delta_nn_per],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig3.update_traces(textfont=dict(size=14), selector=dict(type='waterfall'))

    longo = sum([abs(i) for i in delta_nn_per])

    fig3.update_layout(
    shapes=[dict(
            type="line",
            x0=2.5,
            y0=0,
            x1=2.5,
            y1=longo,
            line=dict(color="grey", width=1)
        ), dict(
            type="line",
            x0=5.5,
            y0=0,
            x1=5.5,
            y1=longo,
            line=dict(color="grey", width=1)
        ), dict(
            type="line",
            x0=-0.5,
            y0=0,
            x1=-0.5,
            y1=longo,
            line=dict(color="grey", width=1)
        ),
    ])

    
    return fig3
#*## Breakout by plan ****
def create_byplan_graph(df_graph):
    df_graph['Quarter'] = df_graph.index.astype(str)
    fig1 = px.bar(df_graph, x = "Quarter", y = 'Revenue', color='Price plan')
    
    return dark_layout(fig1, "Revenue breakout by plan")


