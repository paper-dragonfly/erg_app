from multiprocessing.sharedctypes import Value
import requests
import pandas as pd
from constants import ROOT_URL
import dash_bootstrap_components as dbc
from dash import dcc, html, register_page, callback, Input, Output, State 

register_page(__name__,path_template='/addworkout2/<user_id>')


def layout(user_id='1'):
    return html.Div([
        #Radio Select
        html.Div([
            dcc.Store(id='user_id', data=user_id),
            dcc.Markdown('## Add Workout - Single', id='head_wotype'),
            dcc.RadioItems(options=['Single Time/Distance','Intervals'], value='Single Time/Distance', id='radio_select'),
        # user_input both
            dbc.Row(dcc.Markdown('Date')),
            dbc.Row(dcc.Input('',id="ui_date")),
            dbc.Row([
                dbc.Col(dcc.Markdown('Time')),
                dbc.Col(dcc.Input('hours', id='ui_hours')),
                dbc.Col(dcc.Input('minutes',id='ui_min')),
                dbc.Col(dcc.Input('seconds',id='ui_sec')),
                dbc.Col(dcc.Input('tenths',id='ui_ten'))
                ]),
            dbc.Row(dcc.Markdown('Distance')),
            dbc.Row(dcc.Input('',id='ui_dist')),
            dbc.Row(dcc.Markdown('Split')),
            dbc.Row(dcc.Input('',id='ui_split')),
            dbc.Row(dcc.Markdown('Stroke Rate')),
            dbc.Row(dcc.Input('',id='ui_sr')),
            dbc.Row(dcc.Markdown('Heart Rate')),
            dbc.Row(dcc.Input('',id='ui_hr')),
            dbc.Row(dcc.Markdown('Comment')),
            dbc.Row(dcc.Input('',id='ui_com')),
                # pg1 - single specific
            html.Div([
                dbc.Button('Submit Workout', id='single_submit', n_clicks=0, color='primary'),
                dcc.Store(id='single_data', data={})
                ], id='sing_pg', style={'display':'block'}),
            # pg2 - interval specific
            html.Div([
                dbc.Row(dcc.Markdown('Rest')),
                dbc.Row(dcc.Input('', id='ui_rest')),
                dbc.Button('Submit Interval', id='interval_submit', n_clicks=0, color='primary'),
                dcc.Store(id='interval_data', data={}),
                dbc.Row(
                    [dbc.Table.from_dataframe(pd.DataFrame({}), striped=True, bordered=True)], 
                    id='interval_table'),
                dbc.Button('Submit workout', id='intwo_submit', n_clicks=0, color='primary'),
                ], id='int_pg', style={'display':'none'}), 
            dcc.Markdown('',id='data_json')],
            id='pg_box')
    ])      

# Respond to radio selection
@callback(
    Output('sing_pg', 'style'),
    Output('int_pg', 'style'),
    Input('radio_select', 'value')
)
def choose_page_to_display(choice):
    if choice == 'Single Time/Distance':
        return {'display':'block'}, {'display':'none'}
    return {'display':'none'}, {'display':'block'}

# # Add intervals to inverval table
# @callback(
#     Output('interval_table','children'),
#     Output('df_dict','data'),
#     Input('interval_btn', 'n_clicks'),
#     State('ui_day','value'),
#     State('ui_dist', 'value'),
#     State('ui_time', 'value'),
#     State('df_dict', 'data')
# )
# def add_interval(n_clicks, day, dist, time, df):
#     if n_clicks == 0:
#         return dbc.Table.from_dataframe(pd.DataFrame({'Day':[],'Distance':[], 'Time':[]}), striped=True, bordered=True), {'Day':[],'Distance':[], 'Time':[]}
#     df['Day'].append(day)
#     df['Distance'].append(dist)
#     df['Time'].append(time)
#     return dbc.Table.from_dataframe(pd.DataFrame(df), striped=True, bordered=True), df

# # Add workout to db
# @callback(
#     Output('workout_btn', 'children'),
#     Output('workout_btn', 'color'),
#     Output('data_json', 'children'),
#     Input('workout_btn', 'n_clicks'),
#     State('df_dict', 'data')
# )
# def post_interval_workout(n_clicks, data):
#     if n_clicks == 0:
#         return 'Submit Workout', 'primary', ""
#     json_data = f'{data}'
#     return 'Workout Submitted!', 'success', json_data


# # Pg2 output user_input to alert txt
# @callback(
#     Output('alert_b2','children'),
#     Input('ui_b2', 'value')
# )
# def b2(b2v):
#     return b2v