
import dash
import re
import io
import os
from dash import dcc, html, callback, callback_context as ctx
from dash.dependencies import Input, Output, State
# from dash.dash_table import DataTable, FormatTemplate, Format
# from dash.dash_table.Format import Format, Group
from pages.create_table import *

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import pickle


cwd = os.getcwd()
list_path = os.path.join(cwd, 'data','my_list.pkl')
source_path = os.path.join(cwd, 'data','rf.csv')

dash.register_page(__name__, path='/tagging')

pd.set_option('display.float_format', '{:,.0f}'.format)
 

initial_value = 14940
dark_style =  {'backgroundColor': 'rgba(56, 56, 56, 56)', 'color': 'white'}
html_tag_layout = {     'display':'inline-block'
                       ,'margin-right': '10px' 
                       ,'margin': '5px'          
                       ,'padding-top': '0'       
                       ,'vertical-align': 'center'}

# Load saved categories
with open(list_path, 'rb') as file:
    saved_dict = pickle.load(file)

# Save categories
def save_list(account, my_list):
    with open(list_path, 'wb') as file:
        saved_dict[account] = my_list
        pickle.dump(saved_dict, file)


# Clean numeric columns in input file - replace - with 0
def clean_row_amounts(row):
    try:
        row = row.strip()
        if row=='-': row = row.replace('-', '0')
    except:
        if row=='-': row = row.replace('-', '0')
    return float(row)


# Categorize all rows based on list of keywords
def categorize_rows(row, pre_pair_list_in):
    row = row.replace("FAA_B_R_", "").lower()
    row = row.replace("-", " ").lower()
    row = row.replace("_", " ").lower()
    row = row.split()
    row = ['accrual' if word in ['Accruals','Accrua', 'Accrue','Accru', 'Accr', 'Acc'] else word for word in row]
    row = ['period' if word in ['Perio', 'Peri', 'Per'] else word for word in row]
    row =  ' '.join(row)

    for i in pre_pair_list_in:
        if i in row: return i 
    return 'other'

# Categorize all rows based on list of keywords
def categorize(df_in, account, current_values):
    pattern =     r'\b[A-Za-z]{3}-\d{2}\b'

    # Categorize manual JE
    man_je = (df_in['account']==account) & (df_in['src']=='Manual')
    df_in.loc[man_je , 'category'] = \
    df_in.loc[man_je , 'journal_name'].apply(categorize_rows, args=(current_values,)) 

    # Categorize system entried and mark them as system entires
    sub_je = (df_in['account']==account) & (df_in['src']=='Subledger')
    df_in.loc[sub_je, 'category'] = (
            df_in.loc[sub_je, 'journal_name'].apply(
            lambda x: "SL-"+(re.sub(pattern, '', x)).lstrip()[:-4]) )
    
    df_in['category'] = df_in['category'].apply(lambda x: x.replace('SL-Adjustment', 'SL-Addition'))
    return df_in


# Aggregate by cat_key (mainly category but can be used for other aggreates as well) and return group by dataframe
# Filtered y account if passed
def groupby_categories(df, cat_key='category', acct = None):
    if not isinstance(cat_key, list): cat_key = [cat_key]
    cat_key_usd = cat_key.copy() 
    cat_key_usd.extend(['USD Amt', 'abs'])
    
    if acct is None:
        df_g = df[cat_key_usd].groupby(cat_key).agg({'USD Amt': 'sum'})  
        df_g.reset_index(inplace=True)
    else:
        df_g = df.loc[df['account']==acct, cat_key_usd] \
            .groupby(cat_key).agg({'USD Amt': 'sum', 'abs':'sum'}) 
        
    df_g.sort_values(by=['USD Amt'], inplace=True, ascending=False)
    df_g = df_g[df_g['USD Amt']!=0]
    df_g['abs'] = df_g['USD Amt'].abs()

    return df_g

def create_options_for_account(account):
    try:
        options_out = [dict(label=item, value=item) for item in saved_dict[account]]
        list_out = saved_dict[account]
    except:
        options_out = [{'label':'aws', 'value':'aws'}]
        list_out = []

    return options_out, list_out


# Load  and clean dataframe
df_raw = pd.read_csv(source_path)
df_raw.columns = df_raw.columns.str.strip()
#df_raw.drop(columns=['gl_transaction_key_part','activity_type', 'tax_reclass_2'], inplace=True)
df_raw.drop(columns=['type', 'segment', 'ico'], inplace=True)
df_raw.rename(columns={'company':'co', 'location':'loc', 'cost_center':'cost', 'type':'type', 'Entry Type':'src'}, inplace=True)
df_raw['USD Amt'] = df_raw['USD Amt'].apply(clean_row_amounts).round()
df_raw.insert(5, 'abs', df_raw['USD Amt'].abs())
df_raw.insert(5, 'USD Amt', df_raw.pop('USD Amt'))
df_raw['category'] = 'Other'
df_raw['sort_keys'] = False
df_raw.sort_values(by=['abs'], inplace=True, ascending=False)
df_raw.reset_index(inplace=True, drop=True)


# Initiate data for initial dashbaord load
pre_dict, pre_list = create_options_for_account(initial_value)
df_raw = categorize(df_raw, initial_value, pre_list)

init_base_df = groupby_categories(df_raw[df_raw['account']==initial_value])
init_base_df.sort_values(by=['abs'], inplace=True, ascending=False)

cluster_df = groupby_categories(df_raw[df_raw['account']==initial_value], 'loc')
cluster_df = cluster_df.sort_values(by=['abs'], ascending=False)[:10]



#############
## Define tables
###############

# Main table
# config_dict = dict(exclude_cols= None, dollar_cols=None, numeric_cols=None, percent_cols=None, filter_option=None)
col_setting_dict = { 'numeric_cols': []
                    , 'exclude_cols': ['sort_keys', 'abs', 'period']
                    , 'dollar_cols': ['USD Amt']}

main_table = dash_table_object('base_table', col_setting_dict)
main_table.filter_action = 'native'
main_table.sort_action = 'native'
main_table = main_table.create_table(df_raw[df_raw['account']==initial_value])

# Categories table
category_table = dash_table_object('grouped_table', col_setting_dict)
category_table.sort_action = 'native'
category_table = category_table.create_table(init_base_df)

# Cluster table
cluster_table = dash_table_object('clust_table', col_setting_dict)
cluster_table.sort_action = 'native'
cluster_table = cluster_table.create_table(cluster_df)

#### Graphs

def create_main_result(store_swap, df, account, agg_cat = 'category'):
    df_g_in = groupby_categories(df, agg_cat, account)

    fig3 = go.Figure(
    go.Waterfall(
        name = "2024",
        orientation = "v",
        measure = ['relative'] * len(df_g_in),
        x = df_g_in.index, 
        y = df_g_in['USD Amt'],
        textposition = "auto",
        text = [f'{int(y):,}' for y in df_g_in['USD Amt']],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        textfont=dict(size=14)
        ),
    layout= go.Layout(margin=dict(l=10, r=10, t=0, b=10),  template='plotly_dark'))
    fig3.update_traces(selector=dict(type='waterfall'))

    card_return =  dbc.Card(dcc.Graph(
                        id = 'graph_base',
                        figure=fig3,
                        config={'displayModeBar': False},
                        style={'height': '50vh'})
                    )

    return card_return
    
               
dccg1 = create_main_result(True, df_raw, initial_value,'category')

###################
## Dash core components
###################

dd_cat = dcc.Dropdown(
        id='dropdown', 
        options=pre_dict,
        multi=True,         
        value=pre_list,     # Initial selected values
        clearable=False,
        placeholder="Keyword list for tags is empty",
        style = dark_style 
    )

dd_acc = dcc.Dropdown(
    id='dropdown_acc',
    options=[{'label': g, 'value': g } for g in sorted(list(df_raw['account'].unique()))],
    multi=False,            
    value=initial_value,    # Initial selected values
    clearable=False,
    className='my-dropdown',
    style= ({'width':'300px', 'display':'inline-block', 'margin-right': '5px'
             , 'position':'relative', 'justify-content':'center', "bottom": "0px"
             }| dark_style)
    )

dd_input = dcc.Input(
    id='new-option-label',
    type='text',
    placeholder='Enter new tag',
    style={'display':'inline-block', 'margin-right': '5px'}| dark_style
    )

offcanvas = dbc.Offcanvas(
    [html.H6("Add or remove keywords to use to categorize the data"),
     html.H6("Any line with no associated keyword, is grouped into the Other category"),
    html.Img(src="https://i.ibb.co/LrsYQ0R/help.png", style={"width": "50%", "height": "80%"})],
    id="offcanvas",
    is_open=False,
    placement="top",
    style={"height": "70%"}
)

###################
## Dash layout
###################

# app = dash.Dash(__name__ , external_stylesheets=[dbc.themes.SLATE])
# app.layout = html.Div([

layout = html.Div([
    dbc.Container([
    dbc.Row([
        dbc.Col(width=1),
        dbc.Col(children = [  
            dcc.Download(id="download-dataframe"),
            dd_cat, 
            dd_input,
            dbc.Button( "Add Tag", id="add-option-button",  size="sm", style={'display':'inline-block', 'margin-right': '5px'}),
            dbc.Button('Show/Hide Graph', id='graph_button', size="sm", style={'display':'inline-block', 'margin-right': '5px'}),
            dbc.Button( "Download", id="btn-download", size="sm", style={'display':'inline-block', 'margin-right': '5px'}),
            dbc.Button("How it works", id="open-offcanvas", size="sm", style={'display':'inline-block', 'margin-right': '50px'}, n_clicks=0),
            html.H5("Account: ", style = html_tag_layout), 
            dd_acc], width=11)
    ], align="top"),
    dbc.Row([
          dbc.Col(width=1)
        , dbc.Col(children = [html.H4("Month-over-Month Change")
                            ,  dbc.Collapse(children=[dbc.Card(dccg1), html.Br(), html.Div()], id='collapse', is_open=True)
                            #, html.Br()  
                            , dbc.Card(main_table)
                           ], width=8)
        , dbc.Col(children =[html.H4("Summary")
                            , dbc.Card(category_table)
                            , dbc.Card(html.H4(id='card_total', children='', style={"textAlign": "right"}))
                            , html.H4("Top 15 Regions")
                            , dbc.Card(cluster_table)
                            ], width=3)
    ])], fluid=True)
    , dcc.Store(id='store', data=df_raw.to_dict('records'))
    , dcc.Store(id='active_df', data=df_raw[df_raw['account']==initial_value].to_dict('records'))
    , dbc.Tooltip("Enter new keyword here and click Add Tag", target="new-option-label", placement="top" )
    , dbc.Tooltip("Click here to change the account", target="dropdown_acc", placement="right")
    , dbc.Tooltip("Total month over month change", target="card_total", placement="bottom")
    , dbc.Modal(
            [dbc.ModalHeader(dbc.ModalTitle("No keyword entered")),
            dbc.ModalBody("Please enter a keyword on the input box before clicking Add button")
            ], id="error_msg", is_open=False )
    , offcanvas
])

###################
## Start of callbacks
###################

# Modify total for categories shown in the card in the total section
@callback(
    Output('card_total', 'children'),
    Input(category_table, 'data'))
def callback_update_card(df_in):
    df_out = pd.DataFrame(df_in)
    total = df_out['USD Amt'].sum().round()
    return str('{:,.0f}'.format(total))

# Show graph button
@callback(
    Output('collapse', 'is_open', allow_duplicate=True),
    Input("graph_button", "n_clicks"),
    State("collapse", "is_open"),
    prevent_initial_call= True
)
def callback_toggle_collapse_button(nn, is_open):
    show_graph = not is_open
    return show_graph

# Help button
@callback(
    dash.dependencies.Output("offcanvas", "is_open"),
    dash.dependencies.Input("open-offcanvas", "n_clicks"),
    dash.dependencies.State("offcanvas", "is_open")
)
def toggle_offcanvas(n, is_open):
    if n:
        return not is_open
    return is_open

# Download button
@callback(
    Output("download-dataframe", "data"),
    Input("btn-download", "n_clicks"),
    State(main_table, 'data'),
    State(category_table, 'data'),
    State(cluster_table, 'data'),    
    prevent_initial_call=True
)
def callback_generate_excel(n_clicks, tablea, tableb, tablec):
    buffer = io.BytesIO()
    
    # Write the DataFrame to the buffer as an Excel file
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        pd.DataFrame(tablea).to_excel(writer, index=False, sheet_name='Sheet1')
        pd.DataFrame(tableb).to_excel(writer, index=False, sheet_name='Sheet2')
        pd.DataFrame(tablec).to_excel(writer, index=False, sheet_name='Sheet3')
    
    buffer.seek(0)
    
    return dcc.send_bytes(buffer.getvalue(), "dataframe.xlsx")


# Update based on clicking on the add option button
@callback(
    [Output('dropdown', 'options', allow_duplicate=True),
     Output('dropdown', 'value', allow_duplicate=True),
     #Output('collapse', 'children', allow_duplicate=True), # Update main graph/df.  Might be duplicate update
     #Output(category_table, 'data', allow_duplicate=True), # Might be duplicate update
     Output('active_df', 'data', allow_duplicate=True),
     Output('new-option-label', 'value'),
     Output('error_msg', 'is_open')
     ],
    Input('add-option-button', 'n_clicks'),
    State('active_df', 'data'),
    State('dropdown', 'options'),
    State('dropdown', 'value'),
    State('new-option-label', 'value'),
    State('dropdown_acc', 'value'),
    prevent_initial_call= True

)
def callback_add_option(n_clicks, df_dic, current_options, current_values, new_label, account):
    if new_label is not None and new_label !="":
        new_label = new_label.lower()
        if new_label not in current_options:
            # Add the new option to the existing options
            current_options.append({'label': new_label, 
                                    'value': new_label})
            # Add the new option value to the list of selected values
            current_values.append(new_label)

        else:
            current_values.append(new_label)

        df = categorize(pd.DataFrame(df_dic), account, current_values)
                
        return (current_options, 
                current_values,
                #create_main_result(True, df, account, 'category'),
                #groupby_categories(df).to_dict('records'),
                df.to_dict('records'),
                "",
                False)
    
    else: return dash.no_update, dash.no_update, dash.no_update, dash.no_update, True



# Update based on changing the dropdowns
@callback(
    [Output('collapse', 'children', allow_duplicate=True), # Update main graph/df
    Output('dropdown', 'options', allow_duplicate=True),
    Output('dropdown', 'value', allow_duplicate=True),
    Output(main_table, 'data', allow_duplicate=True),
    Output(category_table, 'data', allow_duplicate=True),
    Output(cluster_table, 'data', allow_duplicate=True),
    Output('active_df', 'data', allow_duplicate=True)
    ],
    [Input('dropdown', 'value'),
     Input('dropdown_acc', 'value')],
     State('dropdown', 'options'),
     State('store', 'data'),
    prevent_initial_call= True
)

def callback_update_after_dropdown(current_values, account, current_options, df_dic):
    df = pd.DataFrame(df_dic)

    if ctx.triggered_id == 'dropdown_acc':
        current_options, current_values = create_options_for_account(account)

    #if isinstance(current_values, dict): current_values = list(current_values

    df = categorize(df, account, current_values)
    save_list(account, current_values)

    df_out = df[df['account']==account]
    cluster_df = groupby_categories(df_out, 'loc')
    cluster_df = cluster_df.sort_values(by=['abs'], ascending=False)[:15]

    return (create_main_result(True, df, account, 'category')
           , current_options
           , current_values
           , df_out.to_dict('records')
           , groupby_categories(df_out).to_dict('records')
           , cluster_df.to_dict('records')
           , df_out.to_dict('records'))
           

#Update graph based on table filtering
@callback(
    Output('collapse', 'is_open', allow_duplicate=True),
    Output('collapse', 'children', allow_duplicate=True),
    Output(main_table, 'data', allow_duplicate=True),
    Output(category_table, 'data', allow_duplicate=True),
    Output(cluster_table, 'data', allow_duplicate=True),
    Input(main_table, 'derived_virtual_data'), 
    Input('graph_base', 'clickData'),
    State('active_df', 'data'),
    State('dropdown_acc', 'value'),
    prevent_initial_call= True)

def callback_update_graph_and_table(rows, clickData, df_dic, account):
    df_in_raw_data = pd.DataFrame(df_dic)    # Raw data
    new_df = pd.DataFrame(rows)              # Filtered data from table
    df_in_raw_data['sort_keys'] = False

    if ctx.triggered_id == 'base_table':
        
        try:

            cluster_df = groupby_categories(new_df, 'loc')
            cluster_df = cluster_df.sort_values(by=['abs'], ascending=False)[:15]
            return (dash.no_update
                    , create_main_result(True, new_df, account, 'category')
                    , dash.no_update
                    , groupby_categories(new_df).to_dict('records')
                    , cluster_df.to_dict('records'))
        except:
             raise dash.exceptions.PreventUpdate
    
    if ctx.triggered_id == 'graph_base':
        try:
            selected_category = clickData['points'][0]['x']
        except: raise dash.exceptions.PreventUpdate
        try:
            df_in_raw_data = df_in_raw_data[df_in_raw_data['account']==account]
            df_in_raw_data.loc[df_in_raw_data['category'] == selected_category, 'sort_keys'] = True
            df_in_raw_data = df_in_raw_data.sort_values(by=['sort_keys', 'category'], ascending=False)

            cluster_df = groupby_categories(df_in_raw_data, 'loc')
            cluster_df = cluster_df.sort_values(by=['abs'], ascending=False)[:15] 

            return  (dash.no_update
                     , dash.no_update
                     , df_in_raw_data.to_dict('records')
                     , dash.no_update
                     , cluster_df.to_dict('records') )
        except:
             raise dash.exceptions.PreventUpdate


# if __name__ == '__main__':
#     app.run_server(debug=True)
