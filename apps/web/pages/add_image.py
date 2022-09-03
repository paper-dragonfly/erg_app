from multiprocessing.sharedctypes import Value
import requests
import pandas as pd
import pdb
from constants import ROOT_URL
import dash_bootstrap_components as dbc
from dash import dcc, html, register_page, callback, Input, Output, State 
from apps.web.dash_fxs import format_and_post_intervals, format_time, duration_to_seconds, post_new_workout, check_date, check_duration, generate_post_wo_dict, format_and_post_intervals
from dash.exceptions import PreventUpdate

register_page(__name__,path_template='/upload_img/<user_id>')

# upload image
# crop
# convert to binary/json
# send data to img processing pipeline
# send back results dict
# populate form with data - make form editable for corrections
# submit workout

# START plotly tutorial

import datetime
import base64

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

register_page(__name__, path='/upload_image')

def layout():
    return dbc.Container([
        dcc.Upload(
            id='upload-image',
            children=html.Button('Upload Image', id="upload_image"),
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-upload'),
    ])

def parse_contents(contents, filename, date):
    return dbc.Container([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@callback(
    Output('output-upload', 'children'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    State('upload-image', 'last_modified'))
def update_output(contents, name, date):
    if contents is not None:
        children = [
            parse_contents(contents, name, date)]
        return children


## END TUTORIAL