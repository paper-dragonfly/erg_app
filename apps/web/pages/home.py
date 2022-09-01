from logging import PlaceHolder
from dash import dcc, html, register_page, Output, Input, State, callback
import dash_bootstrap_components as dbc

register_page(__name__, path='/')

def layout():
    return dbc.Container([
        dcc.Markdown('## Welcome to ErgTracker'),
        dcc.Input(placeholder='wo_id',id='ui_wo_id'),
        dcc.Link('view workout', id='wo_link', href='/details/1')
    ])

@callback(
    Output('wo_link', "href"),
    Input('ui_wo_id', 'value')
)
def create_link(wo_id):
    return f'/details/{wo_id}'

