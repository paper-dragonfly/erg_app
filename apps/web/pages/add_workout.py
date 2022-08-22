import requests
from apps.web.constants import ROOT_URL
from typing import List, Tuple
import dash_bootstrap_components as dbc
from dash import dcc, html, register_page, Input, Output, callback, State
import pdb
import json
from apps.web.dash_fxs import get_name, post_new_workout, duration_to_seconds, input_duration, input_date

register_page(__name__, path_template='/addworkout/<user_id>')
  

def layout(user_id='1'):
    return dbc.Container([
        dbc.Row(children=dcc.Markdown(id = 'title_addworkout', children = '### Add Workout')),
        dcc.Markdown('Guest', id='user_label2'),
        dcc.Markdown(f'{user_id}', id="invisible_id", style={'display':'none'}),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Date (yyyy-mm-dd)', html_for='ui_date'), width=3),
            dbc.Col(children=dcc.Input(id='ui_date', value=""), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Distance (m)', html_for='ui_distance'), width=3),
            dbc.Col(children= dcc.Input(id='ui_distance', value=""), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Time (hh:mm:ss.d)', html_for='ui_time'), width=3),
            dbc.Col(children= dcc.Input(id='ui_time', value=""), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Split (m:ss.d)',html_for='ui_split'), width=3),
            dbc.Col(children= dcc.Input(id='ui_split', value=""), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Intervals', html_for='ui_intervals'), width=3),
            dbc.Col(children= dcc.Input(id='ui_intervals', value=""), width=9)]),
        dbc.Row([
            dbc.Col(children=dbc.Label(children='Comment', html_for='ui_comment'), width=3),
            dbc.Col(children= dcc.Input(id='ui_comment', value=""), width=9)]),
        dbc.Row(children=dbc.Button(id='submit_button', children='submit', n_clicks=0,color='primary')),
        dbc.Row(children=dbc.Alert('Pending', id='status',color='secondary'))
    ])

@callback(
    Output('user_label2', 'children'),
    Input('invisible_id','children')
    )
def display_username(user_id):
    return get_name(user_id).capitalize()

@callback(
    Output('status', 'children'),
    Output('status', 'color'),
    Input('submit_button', 'n_clicks'),
    State('invisible_id','children'),
    State('ui_date','value'),
    State('ui_distance','value'),
    State('ui_time','value'),
    State('ui_split','value'),
    State('ui_intervals','value'),
    State('ui_comment','value')
)
def submit_workout(n_clicks, user_id, wdate, wdistance, wtime, wsplit, wint, wcom):
    #check formatting of date, time, split
    date_formatted:dict = input_date(wdate)
    print('DATE FORMATTED', date_formatted)
    if not date_formatted['accept']:
        return ('Date Formatting Wrong: '+date_formatted['message']), 'danger'
    time_formatted = input_duration(wtime)
    if not time_formatted['accept']:
        return 'Time Formatting Wrong: '+time_formatted['message'], 'danger'
    time = duration_to_seconds(wtime)
    wsplit = '00:0'+wsplit 
    split_formatted = input_duration(wsplit)
    if not split_formatted['accept']:
        return 'Split Formatting Wrong: '+split_formatted['message'], 'danger'
    split = duration_to_seconds(wsplit)
    # post new_workout_data
    data = {'user_id':int(user_id), 'date':wdate, 'distance':int(wdistance), 'time_sec':time,'split':split, 'intervals':int(wint), 'comment':wcom}
    flask_workout_id = post_new_workout(data)
    print('FLASK RESPONSE', flask_workout_id)
    if flask_workout_id['status_code'] == 200:
        return 'Workout Added!','success'
    else:
        return 'Fail', 'danger'

