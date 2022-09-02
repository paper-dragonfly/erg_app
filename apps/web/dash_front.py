from dash import Dash, dcc, html, page_registry, page_container
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from constants import ROOT_URL
import requests
import dash_fxs as dfx
import pdb

app = Dash(__name__,external_stylesheets=[dbc.themes.SANDSTONE], use_pages=True)

user_names = dfx.get_usernames()
wo_id = 9

# Layout
app.layout = html.Div([
    dbc.NavbarSimple([
        dcc.Dropdown(options=user_names, value="guest", id='user_dropdown'),
        dbc.DropdownMenu(
            children=None,
            id='page_menu',
            nav=True,
            label= 'Menu')
        ]),
    dcc.Store(id='wo_id', data=wo_id),
    page_container 
])

#Callback 

@app.callback(
    Output('page_menu', 'children'),
    Input('user_dropdown','value'),
    State('wo_id', 'data')
)
def choose_page(username, wo_id):
    id = dfx.get_id(username.lower())
    pages = [  
        dbc.DropdownMenuItem('Home', href=f'/'),
        dbc.DropdownMenuItem('Workout Log', href=f'/workout_log/{id}'),
        dbc.DropdownMenuItem('Add Workout', href=f'/addworkout/{id}'),
        dbc.DropdownMenuItem('sandbox', href='/sandbox'),
        dbc.DropdownMenuItem('Add New User', href='/newuser'),
        dbc.DropdownMenuItem('Log Table', href=f'/log_table/{id}'),
        dbc.DropdownMenuItem('WOD', href=f'/details/{wo_id}')
    ]
    return pages

if __name__ == '__main__':
    app.run('localhost', 5001, debug=True )