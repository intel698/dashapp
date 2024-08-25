import pickle as pk
import pandas as pd
import numpy as np
import os
from lifelines import KaplanMeierFitter

pd.set_option('display.float_format', lambda x: f'{x:.2f}')

# Load monthly, quarterly and customer detail dataframes
def load():
  cwd = os.getcwd()
  if cwd.endswith('pages'): cwd = os.path.dirname(cwd)

  df_path = os.path.join(cwd, 'data','df.pkl')
  dfq_path = os.path.join(cwd, 'data','dfq.pkl')
  cust_detail_path = os.path.join(cwd, 'data','cust_detail.pkl')

  df = pk.load(open(df_path, 'rb'))
  dfq = pk.load(open(dfq_path, 'rb'))          
  cust_detail = pk.load(open(cust_detail_path, 'rb')) 

  dfq = dfq.assign(
        Basic_Rev = dfq['Basic'] * dfq['Basic Plan'] * 3
      , Standard_Rev = dfq['Standard'] * dfq['Standard Plan'] * 3
      , Premium_Rev = dfq['Premium'] * dfq['Premium Plan'] * 3
  )

  

  return df, dfq, cust_detail
# per_currQ = pd.Period('2022Q4') # Reuturn a list n periods 
def get_period_list(curr_per, n_per):
  return [curr_per - i for i in range(n_per)][::-1]
# Returns "Up" or "Down" and the percentage from an intial and final value
def pct(final, initial):
  tot_c = (float(final) - float(initial))/float(initial)

  if tot_c < 0: return "Down {:.2%}".format(tot_c)
  else: return "Up {:.2%} ".format(tot_c)
   
# This function returns the changes in revenue for the walk
# Input: dataframeQ, current quarter, number of periods to compare
def data_compare_periods(dfq, per_currQ, per_compare):
  per_currQ_prior = per_currQ - per_compare

  change = dfq[dfq.index.isin([per_currQ_prior, per_currQ])].T
  
  # Calculates the difference from the two quarters for all attributes
  change['diff'] = change[per_currQ] - change[per_currQ_prior]
  
  # Change in volume (people) * prior price
  r2 = (
    change.loc['Basic':'Premium','diff'].values *
    change.loc['Basic Plan':'Premium Plan', per_currQ_prior].values
  ) * 3

  # Change in price * current volume (people)
  s2 = (
   change.loc['Basic Plan':'Premium Plan','diff'].values *
   change.loc['Basic':'Premium', (per_currQ)].values
  ) * 3

  # adjustment to plug the difference 
  adjustment = change.at['Subscriber Revenue','diff']/np.sum(r2+s2)
  delta_nn = list(np.stack([r2, s2], axis=0).flatten()*adjustment)
  delta_nn.append(change.at['Variable Revenue','diff'])

  keys = ['Basic add', 'Standard add', 'Premium add', 'Basic price', 'Standard Price', 'Premium Price', 'Variable']
  
  return dict(zip(keys, delta_nn))
# This function calculates the median life of a customer
def calculate_median_duration(cust, per_currM):
  dur_df = cust.sort_values(by=['start'])[['start', 'end','duration']]
  dur_df[['start','end']] = dur_df[['start','end']].astype('period[M]')

  dur_df['duration'] = dur_df.apply(lambda x: (per_currM - x['start']).n 
      if pd.isna(x['duration']) else x['duration'], axis = 1)
  dur_df['event'] =  None
  dur_df.loc[~dur_df['end'].isna(), 'event'] = 1
  dur_df['event'].fillna(0, inplace=True)

  kmf = KaplanMeierFitter()
  kmf.fit(dur_df['duration'], dur_df['event'])

  return  kmf.median_survival_time_
# This function returns the revenue percentage by plan and variable revenue
def pivot_data_by_quarter(dfq):
  per_all_periods_list = pd.period_range(start='2018Q1', end='2023Q1', freq='Q-DEC')
  
  dfq = dfq[['Basic_Rev', 'Standard_Rev', 'Premium_Rev','Variable Revenue' ]]
  dfq.rename(columns={'Variable Revenue':'Variable_Rev'}, inplace=True)
  dfq = dfq[dfq.index.isin(per_all_periods_list)].stack().reset_index()
  dfq.columns = ['Quarter', 'Price plan', 'Revenue']
  dfq.set_index('Quarter', inplace=True)

  return dfq

def get_table_data(dfq, per_currQ):
  period_list = get_period_list(per_currQ, 6)
  dfq = dfq.loc[dfq.index.isin(period_list),
                   ['End_Count', 'End_Count_PoP', 'End_Count_YoY'
                    , 'ARPU', 'Revenue_PoP', 'Revenue_YoY',
                    'Revenue',]]
  
  dfq = dfq[['Revenue', 'Revenue_YoY', 'Revenue_PoP', 'End_Count', 'End_Count_YoY', 'End_Count_PoP', 'ARPU']]
  
  dfq['Revenue'] = dfq['Revenue']/1000
  dfq['Revenue'] = dfq['Revenue'].map('${:,.0f}'.format)
  dfq['Revenue_YoY'] = dfq['Revenue_YoY'].map('{:.2%}'.format)
  dfq['Revenue_PoP'] = dfq['Revenue_PoP'].map('{:.2%}'.format)
  dfq['End_Count'] = dfq['End_Count'].map('{:,.0f}'.format)
  dfq['End_Count_PoP'] = dfq['End_Count_PoP'].map('{:.2%}'.format)
  dfq['End_Count_YoY'] = dfq['End_Count_YoY'].map('{:.2%}'.format)
  dfq['ARPU'] = dfq['ARPU'].map('${:,.0f}'.format)

  dfq.rename(columns={  'Revenue_YoY' :'Y over Y growth %'
                      , 'Revenue_PoP':'Q over Q growth %'
                      , 'End_Count':'Active users'
                      , 'End_Count_PoP':'Q over Q growth %'
                      , 'End_Count_YoY':'Y over Y growth %'
                      , 'ARPU':'ARPU'
                      }, inplace=True)
  
  dfq.index = dfq.index.strftime('%yQ%q')
  return dfq.T.reset_index().rename(columns={'index': '($ in thousands)'})

dfm, dfq, cust_detail = load()
per_currQ = pd.Period('2022Q4')
per_currM = per_currQ.asfreq('M')

df1 = data_compare_periods(dfq, per_currQ, 4)
meadian = calculate_median_duration(cust_detail, per_currM)
df2 = pivot_data_by_quarter(dfq)
df3 = get_table_data(dfq, per_currQ)





