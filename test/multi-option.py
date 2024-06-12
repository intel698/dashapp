import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

# Initial options for the dropdown
initial_options = [
    {'label': 'Option 1', 'value': 'option1'},
    {'label': 'Option 2', 'value': 'option2'},
]

app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=initial_options,
        multi=True,  # Allows multiple selections
        value=[]  # Initial selected values
    ),
    dcc.Input(
        id='new-option-label',
        type='text',
        placeholder='Enter new option label',
    ),
    dcc.Input(
        id='new-option-value',
        type='text',
        placeholder='Enter new option value',
    ),
    html.Button('Add Option', id='add-option-button'),
    html.Div(id='debug-output')  # To display debugging info
])

@app.callback(
    [Output('dropdown', 'options'),
     Output('dropdown', 'value')],
    Input('add-option-button', 'n_clicks'),
    State('dropdown', 'options'),
    State('dropdown', 'value'),
    State('new-option-label', 'value'),
    State('new-option-value', 'value')
)
def add_option(n_clicks, current_options, current_values, new_label, new_value):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    if not new_label or not new_value:
        # Don't add the option if either the label or value is missing
        return current_options, current_values

    # Add the new option to the existing options
    new_option = {'label': new_label, 'value': new_value}
    current_options.append(new_option)

    # Add the new option value to the list of selected values
    current_values.append(new_value)

    return current_options, current_values

if __name__ == '__main__':
    app.run_server(debug=True)
