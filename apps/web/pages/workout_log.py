from dash import dcc, register_page, Output, Input, State, callback, html
import pandas as pd 
import dash_bootstrap_components as dbc
import requests
from typing import List
from constants import ROOT_URL
from apps.web.dash_fxs import flask_requests_get, flask_requests_post
from apps.web.dash_fxs import get_name

register_page(__name__,path_template='/workout_log/<id>')


def layout(id='1'):
    flash_workouts:List[List] = requests.get(ROOT_URL+f'/log/{id}').json()['message']
    workouts = {
        'Date':[],
        'Distance':[],
        'Time':[],
        'Split':[],
        'Intervals':[],
        'Comment':[]
        }
    for i in range(len(flash_workouts)):
        workouts['Date'].append(flash_workouts[i][2]),
        workouts['Distance'].append(flash_workouts[i][3]),
        workouts['Time'].append(flash_workouts[i][4]),
        workouts['Split'].append(flash_workouts[i][5]),
        workouts['Intervals'].append(flash_workouts[i][6]),
        workouts['Comment'].append(flash_workouts[i][7])
    df = pd.DataFrame(workouts)
    return html.Div([
        dcc.Markdown('## Workout Summary Log', id='h1'),
        dcc.Markdown('Guest', id='user_label'),
        dcc.Markdown(f'{id}', id="invisible_id", style={'display':'none'}),
        dbc.Row(children = dbc.Table.from_dataframe(df, striped=True, bordered=True), id = 'log_table')
    ])

@callback(
    Output('user_label', 'children'),
    Input('invisible_id','children')
    )
def display_username(user_id):
    return get_name(user_id).capitalize()
