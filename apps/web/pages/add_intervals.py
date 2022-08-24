from multiprocessing.sharedctypes import Value
import requests
import pandas as pd
from constants import ROOT_URL
import dash_bootstrap_components as dbc
from dash import dcc, html, register_page, callback, Input, Output, State 
from apps.web.dash_fxs import format_time

register_page(__name__,path_template='/addworkout2/<user_id>')

empty_intrvl_table = {'Date':[],'Time':[],'Distance':[],'Split':[],'s/m':[],'HR':[],'Rest':[],'Comment':[]}

def layout(user_id='1'):
    return html.Div([
        #Radio Select
        html.Div([
            dcc.Store(id='user_id', data=user_id),
            dcc.Markdown('## Add Workout - Single', id='head_wotype'),
            dcc.RadioItems(options=['Single Time/Distance','Intervals'], value='Single Time/Distance', id='radio_select'),
        # user_input both
            dbc.Row([
                dbc.Col(dbc.Label('Date',html_for='ui_date'), width=2),
                dbc.Col(dcc.Input('',id="ui_date", size='10'), width=4)
                ]),
            dbc.Row([
                dbc.Col(dbc.Label('Time',html_for='ui_hours'), width=2),
                dbc.Col(dcc.Input(placeholder='hours', id='ui_hours', size='10', maxLength=2), width=2),
                dbc.Col(dcc.Input(placeholder='minutes',id='ui_min',size='10', maxLength=2), width=2),
                dbc.Col(dcc.Input(placeholder='seconds',id='ui_sec',size='10', maxLength=2), width=2),
                dbc.Col(dcc.Input(placeholder='tenths',id='ui_ten',size='10', maxLength=1), width=2)
                ]),
            dbc.Row([
                dbc.Col(dbc.Label('Distance',html_for='ui_dist'), width=2),
                dbc.Col(dcc.Input('',id="ui_dist", size='10'), width=4)
                ]),
            dbc.Row([
                dbc.Col(dbc.Label('Split',html_for='ui_split'), width=2),
                dbc.Col(dcc.Input('',id="ui_split", size='10'), width=4)
                ]),
            dbc.Row([
                dbc.Col(dbc.Label('Stroke Rate',html_for='ui_sr'), width=2),
                dbc.Col(dcc.Input('',id="ui_sr", size='10'), width=4)
                ]),
            dbc.Row([
                dbc.Col(dbc.Label('Heart Rate',html_for='ui_hr'), width=2),
                dbc.Col(dcc.Input('',id="ui_hr", size='10'), width=4)
                ]),
            dbc.Row([
                dbc.Col(dbc.Label('Comment',html_for='ui_com'), width=2),
                dbc.Col(dcc.Input('',id="ui_com", size='10'), width=4)
                ]),
                # pg1 - single specific
            html.Div([
                dbc.Button('Submit Workout', id='single_submit', n_clicks=0, color='primary'),
                dcc.Store(id='single_data', data={})
                ], id='sing_pg', style={'display':'block'}),
            # pg2 - interval specific
            html.Div([
                dbc.Row([
                    dbc.Col(dbc.Label('Rest',html_for='ui_rest'), width=2),
                    dbc.Col(dcc.Input('',id="ui_rest", size='10'), width=4)
                    ]),
                dbc.Button('Submit Interval', id='interval_submit', n_clicks=0, color='primary'),
                dcc.Store(id='int_dict', data={}),
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

# Add intervals to inverval table
@callback(
    Output('interval_table','children'),
    Output('int_dict','data'),
    Input('interval_submit', 'n_clicks'),
    State('ui_date','value'),
    State('ui_hours', 'value'),
    State('ui_min', 'value'),
    State('ui_sec', 'value'),
    State('ui_ten', 'value'),
    State('ui_dist', 'value'),
    State('ui_split', 'value'),
    State('ui_sr', 'value'),
    State('ui_hr', 'value'),
    State('ui_rest', 'value'),
    State('ui_com', 'value'),
    State('int_dict', 'data')
)
def add_interval(n_clicks, date, hours, min, sec, ten, dist, split, sr, hr, rest, com, df):
    if n_clicks == 0:
        return dbc.Table.from_dataframe(pd.DataFrame(empty_intrvl_table), striped=True, bordered=True), {'Date':[],'Time':[],'Distance':[],'Split':[],'s/m':[],'HR':[],'Rest':[],'Comment':[]}
    time = format_time(hours, min, sec, ten)
    df['Date'].append(date)
    df['Time'].append(time)
    df['Distance'].append(dist)
    df['Split'].append(split)
    df['s/m'].append(sr)
    df['HR'].append(hr)
    df['Rest'].append(rest)
    df['Comment'].append(com)
    return dbc.Table.from_dataframe(pd.DataFrame(df), striped=True, bordered=True), df

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