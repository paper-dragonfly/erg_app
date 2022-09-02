import requests
from apps.web.constants import ROOT_URL
from typing import List, Tuple
import dash_bootstrap_components as dbc
from dash import dcc, html, register_page, Input, Output, callback, State
import pdb
import json
from dash.exceptions import PreventUpdate
from apps.web.dash_fxs import get_name, post_new_workout, duration_to_seconds, check_duration, check_date, post_newuser


register_page(__name__, path='/newuser')

# NewUser Traits
# user_name
# dob
# sex
# team

def layout(user_id='1'):
    return dbc.Container([
        dbc.Row(children=dcc.Markdown(id = 'title_newuser', children = '### Add New User')),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='User Name', html_for='ui_name'), width=3),
            dbc.Col(children=dcc.Input(id='ui_name', value=""), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Date of Birth', html_for='ui_dob'), width=3),
            dbc.Col(children= dcc.Input(placeholder="yyyy-mm-dd", id='ui_dob', minLength=10, maxLength=10), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Sex', html_for='ri_sex'), width=3),
            dbc.Col(dcc.RadioItems(['Female', 'Male'], 'Female', inline=True, id="ri_sex"), width=9)
            ]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Team',html_for='dd_team'), width=3),
            dbc.Col(children= dcc.Dropdown(options=['None'], id='dd_team', placeholder='select team'), width=3),
            dbc.Col(children= dcc.Input(placeholder='enter team', id='ui_team', style={"display":"none"}), width=6),
            dcc.Store(id='user_team', data=None)
            ]),
        dbc.Row(children=dbc.Button(id='submit_user_btn',children='Submit User', n_clicks=0,color='primary')),
    ])

@callback(
    Output('dd_team', 'options'),
    Input('dd_team', 'options')
)
def populate_team_dropdown(init_option):
    team_list = requests.get(ROOT_URL+'/listteams').json()['message']
    print(team_list) ###
    team_list.append(init_option[0]) #'None'
    team_list.append('Other')
    return team_list 

@callback(
    Output('ui_team', 'style'),
    Input('dd_team', 'value')
)
def display_team_input(team_selection):
    if team_selection == 'Other':
        return {'display':'block'}
    else:
        raise PreventUpdate

@callback(
    Output('user_team', 'data'),
    Input('dd_team', 'value'),
    Input('ui_team', 'value')
)
def set_user_team(dd, ui):
    if dd == 'Other':
        return ui
    return dd

@callback(
    Output('submit_user_btn', 'children'),
    Output("submit_user_btn", 'color'),
    Input('submit_user_btn', 'n_clicks'),
    State('ui_name', 'value'),
    State('ui_dob', 'value'),
    State('ri_sex', 'value'),
    State('user_team','data')
)
def submit_user(n_clicks, name, dob, sex, team):
    if n_clicks == 0:
        raise PreventUpdate
    newuser_post_dict = {'user_name':None, 'dob':None, 'sex':None, 'team':None}
    newuser_post_dict['user_name'] = name
    newuser_post_dict['dob'] = dob
    newuser_post_dict['sex'] = sex
    newuser_post_dict['team'] = team
    user_id = post_newuser(newuser_post_dict)['user_id']
    return 'User Added', 'success'

# TODO: for some reason user is not posting.  