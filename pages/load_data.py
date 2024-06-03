import pickle as pk
import pandas as pd
import numpy as np

def pct(final, initial):
  tot_c = (float(final) - float(initial))/float(initial)
  
  file_path = "my_text_file.txt"

  # Open the file in append mode
  with open(file_path, "a") as file:
    # Append the variable value followed by a newline
    file.write(str(final) + "\n")
    file.write(str(initial) + "\n")
    file.write(str(tot_c) + "\n")

  if tot_c < 0: return "Down {:.2%}".format(tot_c)
  else: return "Up {:.2%} ".format(tot_c)
   

def load():
    df = pk.load(open('c:\Data\df.pkl', 'rb'))
    dfq = pk.load(open('c:\Data\dfq.pkl', 'rb'))          
    cust_detail = pk.load(open('c:\Data\cust_detail.pkl', 'rb')) 
    #cust = pk.load(open('c:\Data\cust.pkl', 'rb'))  
    return df, dfq, cust_detail

def compare_periods(dfq, per_currQ, per_currQ_prior):
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

# df, dfq, cust_detail = load()