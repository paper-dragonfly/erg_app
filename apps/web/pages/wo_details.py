import pdb
from dash import dcc, register_page, Output, Input, State, callback, html
import pandas as pd 
import dash_bootstrap_components as dbc
import requests
import pdb
from typing import List
from apps.web.constants import ROOT_URL
from apps.web.dash_fns import calc_av_rest, flask_requests_get, flask_requests_post, get_wo_details, wo_details_df
from apps.web.dash_fns import get_name, seconds_to_duration

register_page(__name__, path_template='/details/<wo_id>')

###########
def layout(wo_id='9'):
    df, date, wo_name = wo_details_df(wo_id)
    return dbc.Container([
        dcc.Store(id='wo_id', data=wo_id),
        dcc.Markdown('## Workout Details'),
        dcc.Markdown(f'##### {wo_name}', id='wo_label'),
        dcc.Markdown(f'{date}', id= 'wo_date'),
        dbc.Row([
            dbc.Col(width=1),
            dbc.Col(dbc.Table.from_dataframe(pd.DataFrame(df), striped=True, bordered=True), id="wo_table", align='center'),
            dbc.Col(width=1)
        ])
    ])

# @callback(
#     Output('wo_table', 'children'),
#     Output('wo_label', 'children'),
#     Input('btn1', 'n_clicks'),
#     State('wo_id', 'data')
# )
# def display_wo(nclicks, wo_id):
#     df= {'Time':[], 'Distance':[], 'Split':[], 's/m':[], 'HR':[], 'Rest':[], 'Comment':[]}
#     flask_wo_details = get_wo_details(wo_id)
#     wo_data = flask_wo_details['workout_summary']
#     intrvl_data = flask_wo_details['intervals'] 
#     av_rest = calc_av_rest(intrvl_data)
#     df['Time'].append(wo_data[3]),
#     df['Distance'].append(wo_data[4]),
#     df['Split'].append(wo_data[5]),
#     df['s/m'].append(wo_data[6]),
#     df['HR'].append(wo_data[7]),
#     df['Rest'].append(av_rest),
#     df['Comment'].append(wo_data[9])
#     for i in range(len(intrvl_data)):
#         df['Time'].append(intrvl_data[i][2]),
#         df['Distance'].append(intrvl_data[i][3]),
#         df['Split'].append(intrvl_data[i][4]),
#         df['s/m'].append(intrvl_data[i][5]),
#         df['HR'].append(intrvl_data[i][6]),
#         df['Rest'].append((intrvl_data[i][7])),
#         df['Comment'].append((intrvl_data[i][8]))
#     date = wo_data[2] 
#     # print(df)
#     return dbc.Table.from_dataframe(pd.DataFrame(df), striped=True, bordered=True), date

# Cols: date, time, distance, split, sr, hr, rest, comment
