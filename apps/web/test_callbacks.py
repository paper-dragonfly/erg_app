from conftest import app 
import apps.web.dash_front as dfront
from pytest import raises
from pages.new_user import populate_team_dropdown
import dash_bootstrap_components as dbc
import dash_fxs as dfx
from apps.web.dash_fxs import flask_client_get as client_get, flask_client_post as client_post
from apps.api.logic import db_connect
import apps.web.conftest as c
import pdb
from apps.web.pages.new_user import populate_team_dropdown, display_team_input, set_user_team, submit_user
from dash.exceptions import PreventUpdate

def test_populate_test_db():
    try:
        conn, cur= db_connect('testing', True)
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
    finally:
        cur.close()
        conn.close()

# dash_fxs functions 
def test_get_usernames(client):
    # call fx
    name_list = dfx.get_usernames(get=client_get,get_args={'client':client} )
    assert name_list == ['Kaja', 'Moonshine']



# new_user.py
def test_populate_team_dropdown(client):
    team_list = populate_team_dropdown('None', client_get, {'client':client})
    assert team_list == ['utah crew', 'tumbleweed', 'None', 'Other']


def test_display_team_input():
    assert display_team_input('Other') == {'display':'block'}
    with raises(PreventUpdate):
        display_team_input('fish')

def test_submit_user(client):
    with raises(PreventUpdate):
        submit_user(0,'name','dob','sex','t','p','pa')
    output = submit_user(1,'jam','2000-01-01','Female','tumbleweed',client_post, {'client':client})
    assert output[0] == 'User Added'
    assert output[3] != 0
    output2 = submit_user(1,'jam','2000-01-01','Female','tumbleweed',client_post, {'client':client})
    assert output2[0] == 'Submit User'
    assert output2[2] == {'display':'block'}
    assert output2[3] == 0

    


