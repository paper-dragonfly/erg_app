from dash_front import choose_page 
from pages.new_user import populate_team_dropdown
import dash_bootstrap_components as dbc
import dash_fxs as dfx
from apps.web.dash_fxs import flask_client_get as client_get, flask_client_post as client_post
from apps.api.logic import db_connect
import apps.web.conftest as c
import pdb

# dash_fxs functions 
def test_get_usernames(client):
    try: 
        #populate db with usernames 
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s),(%s,%s)"
        subs = (1,'sam',2,'kat')
        cur.execute(sql, subs)
        # call fx
        name_list = dfx.get_usernames(get=client_get,get_args={'client':client} )
        assert name_list == ['Sam', 'Kat']
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

