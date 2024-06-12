import pandas as pd
from create_data import *
from create_graphs import *
from dash import Input, Output, dcc, html

per_currQ = pd.Period('2022Q4')
per_currM = per_currQ.asfreq('M')
per_month_strftime_Mmm = per_currM.to_timestamp().strftime('%b')

per_list_g1 = period_list(per_currQ, 6)
per_list_g2 = period_list(per_currQ, 5)


df, dfq, cust_detail = load()

#Customer additions per month
lay5 = create_layout("Customer additions per month", "Months", "Number of customers", legend = False)
g5 = create_month_add_graph(lay5, df, per_month_strftime_Mmm, df.at[per_currM, 'Net_add'])

a, b = data_create_avg_life_df(cust_detail)
c = data_transform_plan_df(cust_detail, dfq)

#%%

# Group data by month
box_month_add = [df.loc[df.index.month == i, 'Adds'] for i in range(1, 13)]
box_month_drops = [df.loc[df.index.month == i, 'Drops'] for i in range(1, 13)]
box_p_qtr =  [df.loc[df.index.month.isin(i), 'Net_add'].mean() for i in [[1,2,3],[4,5,6],[7,8,9],[10,11,12]]]

month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'
                , 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_q = [['Jan', 'Feb', 'Mar'], ['Apr', 'May', 'Jun']
            ,['Jul', 'Aug', 'Sep'], ['Oct', 'Nov', 'Dec']]

#%%

# # Create traces for each month
# traces = []
# for i in range(12):
#     trace = go.Violin(
#         y=box_month_add[i],
#         name=month_list[i],
#         box_visible=True,  # Show box plot inside violin
#         meanline_visible=True,  # Show mean line
#         side = 'positive'
#     )
#     traces.append(trace)

# for i in range(12):
#     trace = go.Violin(
#         y=box_month_drops[i],
#         name=month_list[i],
#         box_visible=True,  # Show box plot inside violin
#         meanline_visible=True,  # Show mean line
#         side = 'negative'
#     )
#     traces.append(trace)

# fig = go.Figure()
df['month'] = df.index.month

fig = go.Figure()

fig.add_trace(go.Violin(x=df['month'], #[ df['month'] == i ],
                        y=df['Adds'], #[ df['month'] == i ],
                        #legendgroup='Yes', 
                        #scalegroup='Yes', 
                        name='Adds',
                        side='positive',
                        line_color='blue')
            )
fig.add_trace(go.Violin(x=df['month'], #[ df['month'] == i ],
                        y=df['Drops'], #[ df['month'] == i ],
                        #legendgroup='No', 
                        #scalegroup='No', 
                        name='Drops',
                        side='negative',
                        line_color='orange')
            )
fig.update_traces(meanline_visible=True)
fig.update_layout(violingap=0, violinmode='overlay')
fig.show()
