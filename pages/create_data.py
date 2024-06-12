import pickle as pk
import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter


def period_list(curr_per, n_per): return [curr_per - i for i in range(n_per)][::-1]

def log_variable(*args):
  with open("log.txt", "a") as file:
    for i in range(len(args)):   
      file.write(str(args[i]) + "\n")
    file.write("\n-------------------------------\n")


def pct(final, initial):
  tot_c = (float(final) - float(initial))/float(initial)

  if tot_c < 0: return "Down {:.2%}".format(tot_c)
  else: return "Up {:.2%} ".format(tot_c)
   

def load():
  df = pk.load(open('c:\Data\df.pkl', 'rb'))
  dfq = pk.load(open('c:\Data\dfq.pkl', 'rb'))          
  cust_detail = pk.load(open('c:\Data\cust_detail.pkl', 'rb')) 
  #cust = pk.load(open('c:\Data\cust.pkl', 'rb'))  
  return df, dfq, cust_detail

# This function returns the changes in revenue for the walk
def data_compare_periods(dfq, per_currQ, per_currQ_prior):
  change = dfq[dfq.index.isin([per_currQ_prior, per_currQ])].T
  change['diff'] = change[per_currQ] - change[per_currQ_prior]
  r = change.loc['Basic':'Premium','diff'].values
  r1 = change.loc['Basic Plan':'Premium Plan', per_currQ_prior].values
  r2 = r * r1 * 3
  s = change.loc['Basic Plan':'Premium Plan','diff'].values
  s1 = change.loc['Basic':'Premium', (per_currQ)].values
  s2 = s * s1 * 3

  adjustment = change.at['Subscriber Revenue','diff']/np.stack([r2, s2]).sum()
  delta_nn = ((np.stack([r2, s2], axis=0).reshape(-1,1)).flatten() * adjustment).tolist()
  delta_nn.append(change.at['Variable Revenue','diff'])
  return delta_nn

# This function returns the churn data by customer to use
# for survival analysis and median life
def data_create_avg_life_df(cust):
  dur_df = cust.sort_values(by=['start'])[['start', 'end','duration']]
  dur_df[['start','end']] = dur_df[['start','end']].astype('period[M]')

  dur_df_bin = dur_df['duration'].value_counts(dropna= False).to_frame()
  dur_df_bin['Months in service'] = pd.cut(dur_df_bin.index
                                          , bins=[0, 12, 24, 36, 48, np.inf]
                                          , labels=["0-12", "12-24", "24-36","36-48" ,"Null"])
  dur_df_bin = dur_df_bin.groupby('Months in service', dropna = False).sum()
  dur_df_bin = dur_df_bin.groupby(dur_df_bin.index.fillna('Null')).sum()
  dur_df_bin.index = dur_df_bin.index.add_categories('Active')
  dur_df_bin.index = dur_df_bin.index.fillna('Active')

  dur_df_bin.rename(index={'Null': 'Active'}, inplace=True)
  dur_df_bin['Percentage'] = (dur_df_bin['count']/ dur_df_bin['count'].sum())
  dur_df_bin.style.format({'Percentage': '{:.2%}'})

  return dur_df, dur_df_bin

def calculate_median_duration(df, per_currM):
  df['duration'] = df.apply(lambda x: (per_currM - x['start']).n 
      if pd.isna(x['duration']) else x['duration'], axis = 1)
  df['event'] =  None
  df.loc[~df['end'].isna(), 'event'] = 1
  df['event'].fillna(0, inplace=True)

  kmf = KaplanMeierFitter()
  kmf.fit(df['duration'], df['event'])
  median_life = kmf.median_survival_time_

  if median_life>0: median_life = str(median_life)+ " months"
  else: median_life = "Not reached"
  return median_life

# This function returns the revenue percentage by plan and variable revenue
# 
def data_transform_plan_df(cust_detail, dfq):
  per_all_periods_list = pd.PeriodIndex(['2018Q1', '2018Q2', '2018Q3', '2018Q4', '2019Q1', '2019Q2',
             '2019Q3', '2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4',
             '2021Q1', '2021Q2', '2021Q3', '2021Q4', '2022Q1', '2022Q2',
             '2022Q3', '2022Q4', '2023Q1'],
            dtype='period[Q-DEC]')
  
  a = cust_detail.groupby('plan')[per_all_periods_list].sum().stack().reset_index()
  b = dfq[dfq.index.isin(per_all_periods_list)]['Variable Revenue'].reset_index()
  b.insert(0, "plan", "Variable Revenue")
  a.columns = ['Price plan', 'Quarter', 'Revenue']
  b.columns = ['Price plan', 'Quarter', 'Revenue']
  
  plan_df_stack = pd.concat([a,b], axis=0, ignore_index=True)
  plan_df_stack.set_index('Quarter', inplace=True)
  # df_graph_text['Percentage'] = (df_graph_text['Revenue_x'] / df_graph_text['Revenue_y'])
  # df_graph_text['Percentage'] = df_graph_text['Percentage'].apply(lambda x: "{:.1%}".format(x))
  return plan_df_stack





