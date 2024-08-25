# Dash table object factory
import pandas as pd
from dash.dash_table import DataTable, FormatTemplate, Format
from dash.dash_table.Format import Format
import dash.dash_table.FormatTemplate 
from dash_table.Format import Format, Group, Scheme, Symbol

class dash_table_object:
    """
    Functions:
    1) create_formatting_col: Returns a list of dicitonaries (one dict per column) used to format each column. 
    Each column is defined as a dictioanry :
        {'name' : 'display_name', 
         'id': 'id' ,
         'type': 'numeric',
         'format': format_object
         }
    Different columns have different formatting, if no special formatting, just add id and name

    """

    def __init__(self, table_id: str, config_dict: dict = {}):
        
        self.table_id = table_id                                     
        self.fmt = Format().decimal_delimiter('0').group(Group.yes).groups(3)
        self.config_dict = config_dict
        self.filter_action = 'none'
        self.sort_action = 'none'
        self.style_table = {
            'overflowX': 'auto'
        }
        self.style_filter = {
            'backgroundColor': '#272b30',
            'color': 'white'
        }
        self.style_header = {
            'backgroundColor': '#3e444a',
            'color': 'white',
            'border': '1px solid #3e444a'
        }
        self.style_cell = {
            'textAlign': 'left',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'fontSize': '14px',
            'minWidth': '15px',
            'width': '30px',
            'maxWidth': '500px',
            'backgroundColor': '#272b30',
            'color': 'white',
            'border': '1px solid #3e444a'
        }
        self.style_cell_conditional = [
            {'if': {'column_id': 'USD Amt'},    
             'textAlign': 'right',
             'minWidth': '25px',
             'width': '40px',
             'maxWidth': '100px'
             }]
        self.style_data = {}
        self.style_data_conditional = []
        # self.style_data_conditional = [
        #     {
        #         'if': {'row_index': 'odd'},  # Alternate row colors
        #         'backgroundColor': '#6c757d'  # Slightly darker background for odd rows
        #     }]
        
    def create_table(self, df: pd.DataFrame):
        return  DataTable(
            id=self.table_id,
            data=df.to_dict('records'),
            columns=self.create_formatting_col(list(df.columns), self.config_dict),
            column_selectable=None,
            row_selectable=None,
            sort_action = self.sort_action,
            filter_action= self.filter_action,
            page_size= 25
        , style_table=self.style_table
        , style_filter=self.style_filter
        , style_header=self.style_header

        , style_cell=self.style_cell
        , style_cell_conditional=self.style_cell_conditional

        , style_data=self.style_data
        , style_data_conditional=self.style_data_conditional

        )
    

    def create_formatting_col(self, list_in, config_dict):
        dt_col_list =  []

        for g in list_in:
            if g in config_dict.get('exclude_cols', []): continue     ## Exlclude column from the df
            if g in config_dict.get('dollar_cols', []  ):
                dt_col_list.append({
                            "name": g
                            , "id": g
                            , 'type': 'numeric'
                            , 'format': FormatTemplate.money(0)})
            elif g in config_dict.get('numeric_cols', []):
                dt_col_list.append({
                            "name": g
                            , "id": g
                            , 'type': 'numeric'
                            , 'format': self.fmt})
            elif g in config_dict.get('percent_cols', []):
                dt_col_list.append({
                            "name": g
                            , "id": g
                            , 'type': 'numeric'
                            , 'format': FormatTemplate.percentage(1)})
            else: 
                dt_col_list.append({"name": g, "id": g})
        return dt_col_list