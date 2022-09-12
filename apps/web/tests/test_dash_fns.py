from apps.web.dash_fns import get_name, get_wo_details
from apps.web.dash_fns import get_usernames, flask_client_get as client_get, flask_client_post as client_post, get_id
from apps.api.logic import db_connect
from apps.web.tests.conftest import clear_test_db


def test_00_populate_test_db():
    """
    NOTE: not testing a function
    Add entries to the test db to be used to test all GET functions 
    teams x2, users x2, summ_wo x2, 
    """
    try:
        conn, cur= db_connect('testing', True)
        # populate team
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        # populate users
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
        # populate workout_log
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, time_sec, distance, split, sr, hr, intervals, comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,1,'2000-01-01',120,500,120,26,155,1,'500mx1', 2,1,'2020-02-02',600,2200,122,22,160,2,'5minx2'))
        # populate interval_log
        cur.execute("INSERT INTO interval_log(interval_id, workout_id, time_sec, distance, split, sr, hr, rest, comment, interval_wo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",(1,1,120,500,120,26,155,0,'500mx1',False, 2,2,300,2200,122,22,160,60,'5minx2 i1',True,3,2,300,2200,122,22,160,60,'5minx2 i2',True))
    finally:
        cur.close()
        conn.close()

# GET 
def test_01_get_usernames(client):
    name_list = get_usernames(get=client_get,get_args={'client':client} )
    assert name_list == ['Kaja', 'Moonshine']


def test_02_get_id(client):
    assert get_id('kaja',client_get,{'client':client}) == 1


def test_03_get_name(client):
    assert get_name(1,client_get,{'client':client}) == 'kaja'


def test_04_get_wo_details(client): ##come back
    flask_resp_details = get_wo_details(1,client_get,{'client':client})
    assert flask_resp_details['status_code'] == 200 
    assert flask_resp_details['single'] == True 
    assert len(flask_resp_details['workout_summary']) == 10
    
# def test_clear_testdb():
#     clear_test_db()
    