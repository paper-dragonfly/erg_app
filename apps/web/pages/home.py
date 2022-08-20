from dash import dcc, html, register_page

register_page(__name__, path='/')

def layout():
    return html.Div([
        dcc.Markdown('## Welcome to ErgTracker')
    ])

