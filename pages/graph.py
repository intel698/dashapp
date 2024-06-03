import pandas as pd
import pickle as pk
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pages.load_data import load

df, dfq, cust_detail = load()
DARK_COLOR = 'rgba(0, 0, 0, 0)'

def period_list(curr_per, n_per): return [curr_per - i for i in range(n_per)][::-1]

def create_layout(mtitle = "Title goes here", xtitle="X title", ytitle ="y title", legend = True):
    return go.Layout(
        plot_bgcolor=DARK_COLOR,
        paper_bgcolor=DARK_COLOR,
        template='plotly_dark',
        title=dict(
            text=mtitle,
            font=dict(size=16),
            x=0.5,  # Center the title horizontally
            xanchor='center'),
        xaxis=dict(tickfont=dict(size=12), title=xtitle),
        yaxis=dict(tickfont=dict(size=12), title=ytitle),
        showlegend=legend,
        # margin=dict(l=10, r=10, t=10, b=10),
        )


def dark_layout(fig):
    fig.update_layout(
    plot_bgcolor=DARK_COLOR,
    paper_bgcolor=DARK_COLOR,
    template='plotly_dark')
    return fig

#*## Actual results ****

def create_results_graph(dfqq, columna):

  dfqq.index =  [str(i)[:4] + str(i)[-2:] for i in dfqq.index]

  fig = go.Figure(layout=go.Layout(
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
        #margin=dict(l=40, r=20, t=40, b=10),
        yaxis2=dict(title="Percentage change (%)", overlaying='y', side='right' ,tickformat=',.0%'),  
        showlegend=True)    
  )

  fig.update_traces(texttemplate='%{y:$,.0f}', textfont=dict(size=26))
  fig.add_shape(type="line", x0=0, x1=1, xref="paper", y0=0, y1=0, yref="y2", line=dict(color="Red", width=2,dash="dashdot"))

  fig.add_trace(go.Bar(x=dfqq.index, y=dfqq[columna]))
  fig.add_trace(go.Scatter(x=dfqq.index, y=dfqq[columna+"_PoP"], mode='lines', line=dict(width=5),name='% chg QoQ', yaxis='y2'))  # Specify secondary y-axis
  fig.add_trace(go.Scatter(x=dfqq.index, y=dfqq[columna+"_YoY"], mode='lines', line=dict(width=5),name='% chg YoY', yaxis='y2'))  # Specify secondary y-axis

  return dark_layout(fig)

#*## Breakout by plan ****
def create_byplan_graph(lay1, df_plan_in):
    df_graph = df_plan_in.stack().reset_index()
    df_graph.columns = ['Price plan', 'Quarter', 'Revenue']
    df_graph['Quarter'] = df_graph['Quarter'].astype(str)
    df_graph_text = df_graph.merge( pd.pivot_table(df_graph, index='Quarter', values='Revenue',aggfunc='sum'), on='Quarter', how='left')
    df_graph_text['Percentage'] = (df_graph_text['Revenue_x'] / df_graph_text['Revenue_y'])
    df_graph_text['Percentage'] = df_graph_text['Percentage'].apply(lambda x: "{:.1%}".format(x))
    
    fig1 = go.Figure(layout = lay1)
    fig1.add_trace(go.Bar(x = df_graph_text["Quarter"], y = df_graph_text['Revenue_x']))
   
    return fig1

#*#  Profile of customer profile
def create_customer_profile_graph(df_in_g3):

    fig2=px.bar(df_in_g3, x="duration", y="household", color="plan", title= "Customer Profile")
    fig2.update_layout(
        legend=dict(
        x=0,
        y=1,
        bordercolor="Black",
        borderwidth=2)
    )
    return fig2

#*# Waterfall chart to compare period over period
def create_compare_graph(lay3, delta_nn_per):
    list_waterfall = ['Basic', 'Standard', 'Premium', 'Basic Plan'
                      , 'Std Plan', 'Prem Plan', 'Var Revenue']
    fig3 = go.Figure(layout= lay3)
    fig3.add_trace(go.Waterfall(
        name = "2024",
        orientation = "v",
        measure = ['relative'] * 7,
        x = [['--Change in active customers--','--Change in active customers--','--Change in active customers--'
            ,'-----Change in price-----','-----Change in price-----','-----Change in price-----','--Other--'], list_waterfall],
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

#*# Number of customers additions per period
def create_month_add_graph(lay, df, mes, cantidad):

    # Group data by month
    box_p_month = [df.loc[df.index.month == i, 'Net_add'] for i in range(1, 13)]
    box_p_qtr =  [df.loc[df.index.month.isin(i), 'Net_add'].mean() for i in [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]]

    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_q = [['Jan', 'Feb', 'Mar'], ['Apr', 'May', 'Jun'],['Jul', 'Aug', 'Sep'], ['Oct', 'Nov', 'Dec']]

    # Create traces for each month
    traces = []
    for i in range(12):
        trace = go.Violin(
            y=box_p_month[i],
            name=month_list[i],
            box_visible=True,  # Show box plot inside violin
            #points='all',      # Display all points
            meanline_visible=True,  # Show mean line
            line_color='blue'  # Set color of the violin plot
        )
        traces.append(trace)

    # Add mean line for each quarter
    for ge in range(4):
        mean_line = go.Scatter(x=month_q[ge], y=box_p_qtr[ge] * np.ones(3)
                               , mode='lines',line=dict(color='red', dash='dash'))
        traces.append(mean_line)


    # Add point to the plot
    blue_point = go.Scatter(
        x=[mes],  # Display the blue point in June
        y=[cantidad],    # Display at y=1000
        mode='markers+text',
        marker=dict(color='orange', size=10),
        text='Current month addition',
        textposition='top center'
    )
    traces.append(blue_point)

    # Create the figure
    return go.Figure(data=traces, layout=lay)



# per_currQ = pd.Period('2022Q4')
# per_currM = pd.Period('2022-12')
# per_list_g1 = period_list(per_currQ, 8)
# per_list_g2 = period_list(per_currQ, 5)

# g1 = dfq[dfq.index.isin(per_list_g1)]
# create_results_graph(g1, 'Revenue').show()
# create_results_graph(g1, 'End_Count').show()

# g2 = cust_detail.groupby('hotspot')[per_list_g2].sum()
# create_byplan_graph(g2).show()

# g3 = cust_detail[cust_detail[per_currQ]!=0].groupby(['hotspot'
#         , 'Household','duration'])[per_currQ].count().reset_index()
# create_customer_profile_graph(g3).show()

# g4 = compare_periods(dfq, per_currQ, per_currQ-4)
# create_compare_graph(g4).show()

# g5 = df
# create_month_add_graph(g5, 'Jun', 1200).show()