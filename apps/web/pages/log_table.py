from dash import Dash, dash_table, dcc, html, register_page, callback
from dash.dependencies import Input, Output
import pandas as pd
import requests
from typing import List
from constants import ROOT_URL
from apps.web.dash_fxs import flask_requests_get, flask_requests_post
from apps.web.dash_fxs import get_name, seconds_to_duration
import dash_bootstrap_components as dbc

register_page(__name__,path_template='/log_table/<user_id>')


def layout(user_id=1):
    flash_workouts:List[List] = requests.get(ROOT_URL+f'/log/{user_id}').json()['message']
    workouts = {
        'id' : [],
        'Date':[],
        'Time': [],
        'Distance':[],
        'Split':[],
        'Stroke Rate': [],
        'Heart Rate': [],
        'Intervals':[],
        'Comment':[]
        }
    for i in range(len(flash_workouts)):
        workouts['id'].append(flash_workouts[i][0]),
        workouts['Date'].append(flash_workouts[i][2]),
        workouts['Time'].append(seconds_to_duration(flash_workouts[i][3])),
        workouts['Distance'].append(str(flash_workouts[i][4])),
        workouts['Split'].append(seconds_to_duration(flash_workouts[i][5])),
        workouts['Stroke Rate'].append(str(flash_workouts[i][6])),
        workouts['Heart Rate'].append(str(flash_workouts[i][7])),
        workouts['Intervals'].append(str(flash_workouts[i][8])),
        workouts['Comment'].append(flash_workouts[i][9])

    df = pd.DataFrame(workouts)
    df.set_index('id', inplace=True, drop=False)

    return dbc.Container([
        dash_table.DataTable(
            id='table',
            columns=[{"name": k, "id": k, "deletable": False, "selectable": True} for k in df if k !='id'],
            data=df.to_dict('records'),
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            # column_selectable="single",
            row_selectable="single",
            # row_deletable=True,
            # selected_columns=[],
            # selected_rows=[],
            selected_row_ids=[],
            page_action="native",
            page_current= 0,
            page_size= 10
            ),
        dbc.Button('Select Row', id='btn_view_details', n_clicks=0,color='secondary', href=None)
    # html.Div(id='datatable-interactivity-container')
    ])

@callback(
    Output('btn_view_details', 'children'),
    Output('btn_view_details', 'color'),
    Output('btn_view_details','href'),
    Input('table', 'selected_row_ids')
)
def show_id(selected_id):
    if len(selected_id) == 0:
        return 'Select Row', 'secondary', None
    return 'View Workout Details', 'warning', f'/details/{selected_id[0]}' 




