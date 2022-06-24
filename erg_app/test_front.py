from erg_app import erg_front as front
from erg_app.constants import ROOT_URL
from erg_app.logic import db_connect
import erg_app.conftest as c 
import unittest 
from unittest.mock import MagicMock, patch 
import pdb

#TODO: add two spaces between func definitions 
# TODO: change order of args in mock
#TODO rewrite mock - remove loop in mock, make for loop in outter func 
# TODO: rename mock
# TODO: use patch in mock
def mock(input_values:list,func, **kwargs):
    output = []
    printed = []
    # patch input() so that when called next value in output:lst is submitted 
    front.input = lambda _ : input_values.pop(0)
    # patch print() so when called str is appended to printed:lst
    front.print = lambda s : printed.append(s)
    while input_values:
        out = func(**kwargs) 
        output.append(out)
    return output, printed

def test_duration_to_seconds():
    secs = front.duration_to_seconds('00:01:40.00')
    assert secs == 100

def test_input_sex():
    output, printed = mock(["M",'f','house',""], front.input_sex, prompt_str="")
    assert output == ['M','F',""]
    assert printed == ['Must select M or F']

def test_input_int():
    output, printed= mock(['2',"",'five','1'], front.input_int, prompt_str="")
    assert output == [2,"",1]
    assert printed == ['Input must be integer']

def test_input_duration():
    output, printed = mock(['01:00:20.55','00:15:00', 'fish', '25:00:00.00','00:01:002', '00:02:23.aa', '01:01:01.01'], front.input_duration, prompt_str="")
    assert output == ['01:00:20.55','00:15:00.00', '01:01:01.01'] 
    assert printed == ['Must use hh:mm:ss.dd formatting','hours out of range', 'Input length incorrect', 'ms formatting incorrect']

def test_input_date():
    output, printed = mock(['2000-02-30','2000-01-32','2000-15-01','2000/01/01','2000-01-01'], front.input_date, prompt_str="")
    assert output == ['2000-01-01']
    assert printed == ['day out of range','day out of range','month out of range','Must use yyyy-mm-dd formatting']

def test_input_interval_type():
    output, printed = mock(['fish','DARK', 'distance'], front.input_interval_type, prompt_str="")
    assert output == ['distance', 'distance']
    assert printed == ['Invalid entry, try agian']
    # anything starting with d or t will be converted to a valid entry. I'm ok with this. 

def test_create_new_workout_dict():
    output, printed = mock(['2000-01-01','2000','00:08:00.00','00:02:00.00','3','2k'],front.create_new_workout_dict,workout_type=3,user_id=1)
    assert output == [{'user_id':1,'date':'2000-01-01','distance':2000,'time_sec':480, 'split':120, 'intervals':3,'comment':'2k' }]
    assert printed == [] 

    output, printed = mock(['2000-01-01','2000','00:08:00.00','00:02:00.00','2k'],front.create_new_workout_dict,workout_type=1,user_id=1)
    assert output == [{'user_id':1,'date':'2000-01-01','distance':2000,'time_sec':480, 'split':120, 'intervals':1,'comment':'2k' }]
    assert printed == [] 

def test_create_intervals_dict():
    mock_inputs = [12000,'01:30:00.00','00:02:10.00', '00:01:00']
    output, printed = mock(mock_inputs, front.create_intervals_dict,workout_id=1,interval=2, interval_type='distance')
    assert output == [{'workout_id':1,'interval_type':'distance','distance':12000,'time_sec':5400,'split':130,'rest':60}]
    assert printed == ['Interval 2'] 

def test_create_logsearch_dict():
    mock_inputs = ['2000-01-01',24000,"",""]
    output, printed = mock(mock_inputs, front.create_logsearch_dict)
    assert output == [{'date':'2000-01-01','distance':24000}]
    assert printed == ['Search by different parameters, press enter to skip a param'] 

    mock_inputs = ["","","",""]
    output, printed = mock(mock_inputs, front.create_logsearch_dict)
    assert output == [{}]
    assert printed == ['Search by different parameters, press enter to skip a param'] 

    mock_inputs = ["2000-17-01",'2000-01-01',"","",""]
    output, printed = mock(mock_inputs, front.create_logsearch_dict)
    assert output == [{'date':'2000-01-01'}]
    assert printed == ['Search by different parameters, press enter to skip a param','month out of range'] 

def test_login(client):
    try: 
        #populate db with user 
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(5,'sasha'))
        # call login()
        output, printed = mock(
            ['2','sasha'], 
            front.login,
            get=front.flask_client_get,
            get_args={'client':client},
            post=front.flask_client_post,
            post_args={'client':client})
        assert output == [(5, 'sasha')]
        assert printed == ['\nLOGIN', '1. List Users \n2. Search by User Name', "sasha logged in" ]  
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()

    
def test_create_new_user(client):
    try:
        conn, cur = db_connect('testing', True)
        output, printed = mock(
            ['brook',14,'F','UtahCrew'],
            front.create_new_user,
            post=front.flask_client_post,
            post_args={'client': client})
        cur.execute("SELECT user_id FROM users WHERE user_name = 'brook'")
        brook_id = cur.fetchone()[0]
        assert output == [(brook_id, 'brook')]
        assert printed == ['\nCreate New User','\nNew user created. Welcome brook']
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()


# def test_authenticate(client): # don't think I can do this because can't pass input_values into the sub-functions of login and creae_new_user so getting 'can't pop from empty list error'
#     # TODO check with NICO if there's a fix, if not remove excess args from authenticate
#     try:
#         #populate db with user 
#         conn, cur = db_connect('testing', True)
#         cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(6,'bruno'))
#         conn,cur = db_connect('testing',True)
#         output, printed = mock(
#             #[incorrect input, select to login, select to list users,user_name]
#             ['1','1','bruno'],
#             front.authenticate,
#             login_get=front.flask_client_get,
#             login_get_args={'client':client},
#             new_user_post= front.flask_client_post,
#             new_user_post_args={'client':client})
#         assert output == [(6,'bruno')]
#         assert printed ==["\nWelcome to ErgTracker \n1.Login\n2.Create new account",'pick an option using the coresponding bullet number','\nLOGIN', '1. List Users \n2. Search by User Name', "bruno logged in"]
#     finally: 
#         cur.close()
#         conn.close()
#         c.clear_test_db()


def test_view_workout_log(client):
    # populate db with user and workouts
    try:
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s,%s)",(7,'emma'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec,split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,7,'2022-01-01', 2000,480,120,1,'PR'))
        # check returns expected
        assert front.view_workout_log(7,'emma',post=front.flask_client_post,post_args={'client':client}) == [["workout_id","user_id","date","distance","time_sec","split","intervals","comment"],[1,7,'2022-01-01',2000,480,120,1,'PR']]
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()   

def interval_patch(a,i,b):
    int_dict = {"time_sec":[130,125,120,115,110], 'split':[130,125,120,115,110]}
    return {'workout_id':2,'interval_type':'distance', 'distance':500, 'time_sec':int_dict['time_sec'][i], 'split':int_dict['split'][i], 'rest':60} 

# TODO: finish test for when there are intervals
def test_add_workout(client):
    # populate db
    try: 
        # populate db with user and single time workout
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id,user_name) VALUES(8,'simon')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(1,8,'2000-01-01',2000,480,120,1,'2k')")
        # add interval workout to db
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(2,8,'2000-01-02',2000,480,120,4,'4x500m')") 
        cur.execute("INSERT INTO interval_log(interval_id,workout_id,interval_type,distance,time_sec,split,rest) VALUES(1,2,'distance',500,130,130,60),(2,2,'distance',500,125,125,60),(3,2,'distance',500,115,115,60),(4,2,'distance',500,110,110,60)")
        # create mock values and patches
        mock_workout_dict = {'user_id':8,'date':'2000-01-01','distance':2000,'time_sec':480, 'split':120, 'intervals':1,'comment':'2k' }
        with patch('erg_app.erg_front.input_int', return_value=2):#single distance
            with patch('erg_app.erg_front.create_new_workout_dict', return_value=mock_workout_dict):
                r_val:dict = front.add_workout(8,post=front.flask_client_post, post_args={'client':client}) 
                # assert response is as expected
                assert r_val['status_code'] == 200 
                assert type(r_val['workout_id']) == int
        with patch('erg_app.erg_front.input_int',return_value=4): #interval distance
            mock_workout_dict2 = {'user_id':8, 'date':'2000-01-02','distance':2000,'time_sec':480,'split':120,"intervals": 4,'comment':'4x500m'}
            with patch('erg_app.erg_front.create_new_workout_dict', return_value = mock_workout_dict2): 
                with patch('erg_app.erg_front.input_interval_type', return_value='distance'): 
                    with patch('erg_app.erg_front.create_intervals_dict', side_effect=interval_patch):
                        r_val = front.add_workout(8,post=front.flask_client_post,post_args={'client':client})
                        assert r_val['status_code'] == 200
                        assert r_val['message'] == [True,True,True,True]   
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

def test_display_interval_details(client):
    try: 
        # populate db with user and workouts
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id,user_name) VALUES(9,'gerry')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(1,9,'2000-01-01',2000,480,120,1,'2k')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(2,9,'2000-01-02',2000,480,120,4,'4x500m')") 
        # Add intervals 4x500m
        cur.execute("Insert INTO interval_log(interval_id,workout_id,interval_type,distance,time_sec,split,rest) VALUES(1,2,'distance',500,130,130,60),(2,2,'distance',500,125,125,60),(3,2,'distance',500,115,115,60),(4,2,'distance',500,110,110,60)")
        # make flask post call
        r_val = front.display_interval_details(2,post=front.flask_client_post,post_args={'client':client})
        assert len(r_val)==5
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_search_log(client):
    try: 
        # populate db with user and workouts
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id,user_name) VALUES(9,'hannah')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(1,9,'2000-01-01',2000,480,120,1,'2k')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(2,9,'2000-01-02',2000,480,120,4,'4x500m')") 
        cur.execute("Insert INTO interval_log(interval_id,workout_id,interval_type,distance,time_sec,split,rest) VALUES(1,2,'distance',500,130,130,60),(2,2,'distance',500,125,125,60),(3,2,'distance',500,115,115,60),(4,2,'distance',500,110,110,60)")
        # TEST WITHOUT INTERVAL DETAILS
        #patch inner func and assert response is as expected
        search_dict = {'date':'2000-01-01', 'distance':2000}
        with patch('erg_app.erg_front.input_int', return_value=""):#skip looking at interval details
            with patch('erg_app.erg_front.create_logsearch_dict', return_value=search_dict):
                r_val = front.search_log(post=front.flask_client_post,post_args={'client':client})
                assert len(r_val) == 2
                assert '2k' in r_val[1]
            search_dict = {'distance':2000}
            with patch('erg_app.erg_front.create_logsearch_dict', return_value=search_dict):
                r_val = front.search_log(post=front.flask_client_post,post_args={'client':client})
                assert len(r_val) == 3
            search_dict = {'distance':4000}
            with patch('erg_app.erg_front.create_logsearch_dict', return_value=search_dict):
                r_val = front.search_log(post=front.flask_client_post,post_args={'client':client})
                assert len(r_val) == 0
        # TEST WITH INTERVAL DETAILS
        with patch('erg_app.erg_front.create_logsearch_dict', return_value={'distance':2000}):#all workouts
            with patch('erg_app.erg_front.input_int', return_value=2):#view interval details for workout where workout_id == 2
                r_val = front.search_log(post=front.flask_client_post,post_args={'client':client})
                assert len(r_val['workout_summary']) == 3
                assert len(r_val['interval_details']) == 5
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_view_user_stats(client):
    try: 
        # populate db with user and workouts
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id,user_name) VALUES(10,'paul')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(1,10,'2000-01-01',2000,480,120,1,'2k')")
        cur.execute("INSERT INTO workout_log(workout_id,user_id,date,distance,time_sec,split,intervals,comment) VALUES(2,10,'2000-01-02',2000,480,120,4,'4x500m')") 
        #call func assert return is expected
        r_val = front.view_user_stats(10,post=front.flask_client_post,post_args={'client':client})
        assert r_val[1][0] == 4000
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

def test_run():
    pass 







