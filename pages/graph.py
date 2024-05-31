import pandas as pd
import pickle as pk
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

df = pk.load(open('c:\Data\df.pkl', 'rb'))
dfq = pk.load(open('c:\Data\dfq.pkl', 'rb'))          

#cust = pk.load(open('c:\Data\cust.pkl', 'rb'))  
cust_detail = pk.load(open('c:\Data\cust_detail.pkl', 'rb')) 


def period_list(curr_per, n_per): return [curr_per - i for i in range(n_per)][::-1]

def create_results_graph(dfqq, columna):
  
  dfqq.index =  [str(i)[:4] + str(i)[-2:] for i in dfqq.index]

  fig = go.Figure()
  fig.update_layout(
      yaxis2=dict(title='Number of Customers', overlaying='y', side='right', tickformat=',.0%'),  # Secondary y-axis (for line)
      title_font=dict(size=16),
      yaxis_title_font=dict(size=14),
      xaxis_title_font=dict(size=14),
      yaxis=dict(tickfont=dict(size=12), title='Bar Values'),
      xaxis=dict(tickfont=dict(size=12)),
      margin=dict(l=80, r=40, t=80, b=30),
      plot_bgcolor='white',
      paper_bgcolor='white',
      showlegend=True
  )

  fig.update_traces(texttemplate='%{y:$,.0f}', textfont=dict(size=26))
  fig.add_trace(go.Bar(x=dfqq.index, y=dfqq[columna], name=columna))
  fig.add_shape(type="line", x0=0, x1=1, xref="paper", y0=0, y1=0, yref="y2",
    line=dict(
        color="Red",
        width=2,
        dash="dashdot",
    ))

  fig.add_trace(go.Scatter(x=dfqq.index, y=dfqq[columna+"_PoP"], mode='lines', line=dict(width=5),name='% chg QoQ', yaxis='y2'))  # Specify secondary y-axis
  fig.add_trace(go.Scatter(x=dfqq.index, y=dfqq[columna+"_YoY"], mode='lines', line=dict(width=5),name='% chg YoY', yaxis='y2'))  # Specify secondary y-axis

  return fig

#df_plan = cust_detail.groupby('hotspot')[per_list].sum()
# df_plan.loc['Variable Revenue'] = new_row = dfq[dfq.index.isin(per_list)]['Var_rev'].tolist()
# pd.concat([df_plan, df_plan.sum(axis=0).to_frame(name = 'Total Revenue').T])

def create_byplan_graph(df_plan_in):
    df_graph = df_plan_in.stack().reset_index()
    df_graph.columns = ['Price plan', 'Quarter', 'Revenue']
    df_graph['Quarter'] = df_graph['Quarter'].astype(str)
    df_graph_text = df_graph.merge( pd.pivot_table(df_graph, index='Quarter', values='Revenue',aggfunc='sum'), on='Quarter', how='left')
    df_graph_text['Percentage'] = (df_graph_text['Revenue_x'] / df_graph_text['Revenue_y'])
    df_graph_text['Percentage'] = df_graph_text['Percentage'].apply(lambda x: "{:.1%}".format(x))
    fig1 = px.bar(df_graph_text, x="Quarter", y='Revenue_x', color="Price plan", title="Revenue by Price Plan", text = 'Percentage')
    return fig1


def create_customer_profile_graph(df_in_g3):

    fig2=px.bar(df_in_g3, x="duration", y="Household", color="hotspot").update_layout(title="Customer Profile")
    fig2.update_xaxes(title_text='Customer tenure in months')
    fig2.update_yaxes(title_text='Number of customers')
    return fig2

def compare_periods(dfq, per_currQ, per_currQ_prior):
  change = dfq[dfq.index.isin([per_currQ_prior, per_currQ])].T
  change['diff'] = change[per_currQ] - change[per_currQ_prior]
  r = change.loc['Affordable':'Premium','diff'].values
  r1 = change.loc['Affordable_Price':'Premium_Price', per_currQ_prior].values
  r2 = r * r1 * 3
  s = change.loc['Affordable_Price':'Premium_Price','diff'].values
  s1 = change.loc['Affordable':'Premium', (per_currQ)].values
  s2 = s * s1 * 3

  adjustment = change.at['Subscriber Revenue','diff']/np.stack([r2, s2]).sum()
  #adjustment = 1
  delta_nn = ((np.stack([r2, s2], axis=0).reshape(-1,1)).flatten() * adjustment).tolist()
  delta_nn.append(change.at['Var_rev','diff'])
  return delta_nn

def create_compare_graph(delta_nn_per):
    list_waterfall = ['Affordable', 'Standard', 'Premium', 'Affordable_Price'
                      , 'Standard_Price', 'Premium_Price', 'Var_rev']
    fig4 = go.Figure(go.Waterfall(
        name = "2024",
        orientation = "v",
        measure = ['relative'] * 7,
        x = [['Change in active customers','Change in active customers','Change in active customers'
            ,'Change in price','Change in price','Change in price','Other'], list_waterfall],
        y = delta_nn_per,
        textposition = "outside",
        text = [f'{int(y):,}' for y in delta_nn_per],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig4.update_traces(textfont=dict(size=14), selector=dict(type='waterfall'))
    fig4.update_xaxes(title_font=dict(size=14))

    return fig4

def create_month_add_graph(df, mes, cantidad):

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
            points='all',      # Display all points
            meanline_visible=True,  # Show mean line
            line_color='blue'  # Set color of the violin plot
        )
        traces.append(trace)

    # Layout settings
    layout = go.Layout(
        title='Monthly Net Customer Additions ',
        xaxis=dict(title='Months'),
        yaxis=dict(title='Net Additions'),
        showlegend=False
    )

    # Add mean line for each quarter
    for ge in range(4):
        mean_line = go.Scatter(x=month_q[ge], y=box_p_qtr[ge] * np.ones(3), mode='lines',line=dict(color='red', dash='dash'))
        traces.append(mean_line)


    # Add blue point to the plot
    blue_point = go.Scatter(
        x=[mes],  # Display the blue point in June
        y=[cantidad],    # Display at y=1000
        mode='markers',
        marker=dict(color='orange', size=10),
        name='Blue Point'
    )
    traces.append(blue_point)

    # Create the figure
    return go.Figure(data=traces, layout=layout)



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