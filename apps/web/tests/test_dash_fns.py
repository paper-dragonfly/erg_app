from dash_fns import get_usernames, flask_client_get as client_get, flask_client_post as client_post
from apps.api.logic import db_connect


def test_00_populate_test_db():
    """
    NOTE: not testing a function
    Add entries to the test db to be used to test all GET functions 
    """
    try:
        conn, cur= db_connect('testing', True)
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
    finally:
        cur.close()
        conn.close()

# GET 
def test_001_get_usernames(client):
    name_list = get_usernames(get=client_get,get_args={'client':client} )
    assert name_list == ['Kaja', 'Moonshine']
