from dash import Dash, dcc, html, page_registry, page_container
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from constants import ROOT_URL
import requests
import dash_fxs as dfx
import pdb

app = Dash(__name__,external_stylesheets=[dbc.themes.SANDSTONE], use_pages=True)

# Components
user_names = dfx.get_usernames()
navbar = dbc.NavbarSimple([
    dcc.Dropdown(options=user_names, value="guest", id='user_dropdown'),
    dbc.DropdownMenu(
        children=None,
        id='page_menu',
        nav=True,
        label= 'Menu')
    ])
# Layout
app.layout = dbc.Container([
    navbar, page_container
])

#Callback 

@app.callback(
    Output('page_menu', 'children'),
    Input('user_dropdown','value')
)
def choose_page(username):
    id = dfx.get_id(username.lower())
    pages = [  
        dbc.DropdownMenuItem('Home', href=f'/'),
        dbc.DropdownMenuItem('Workout Log', href=f'/workout_log/{id}'),
        dbc.DropdownMenuItem('Add Workout', href=f'/addworkout/{id}'),
        dbc.DropdownMenuItem('sandbox', href='/sandbox'),
        dbc.DropdownMenuItem('Add New User', href='/newuser')
        # dbc.DropdownMenuItem('Add Int', href=f'/addworkout2/{id}'),
    ]
    return pages

if __name__ == '__main__':
    app.run('localhost', 5001, debug=True )