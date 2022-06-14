import json 
from erg_app import conftest as c
from erg_app.logic import add_new_user, db_connect, get_user_id, search_sql_str, add_workout, add_interval
from pydantic import BaseModel
import pdb
from erg_app.post_classes import NewUser, NewInterval, NewWorkout


def test_get_user_id():
    """
    GIVEN a user_name
    WHEN user_name and db_name are passed to get_user_id() 
    THEN assert expected user_id is returned
    """
    try: 
        # populate db with user if not exists
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(1,'kaja'))
        # use f(x) to get id
        assert get_user_id('kaja', 'testing') == 1
    finally: 
        c.clear_test_db()
        cur.close()
        conn.close()

def test_userid(client):
    """
    GIVEN a flask app 
    WHEN POST submits a user_name
    THEN assert that the returned user_id is as expected
    """
    try: 
        #populate db with user 
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(1,'kaja'))
        # send POST request for user_id 
        response = client.post("/userid", data=json.dumps({"user_name":"kaja"}), content_type='application/json') 
        assert response.status_code == 200
        #type(response.data)==byte, type(response.data.decode("ASCII"))==str, type(json.loads(...))==dict
        data_dic = json.loads(response.data.decode("ASCII"))
        assert data_dic['user_id'] == 1
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()


def test_add_new_user():
    """
    GIVEN an attempt to make a new user
    WHEN a NewUser instance is passed to add_new_user(db, NewUser)
    THEN assert there is a singel entry in the db that matches that new user
    """
    #create NewUser instance
    test_user = NewUser(user_name='nico',pw='mypw', sex='M',age=30,team='tumbleweed',weight=180)
    #pass to add_new_user()
    user_id = add_new_user('testing',test_user)
    # get test_user data from db 
    try: 
        conn, cur = db_connect('testing')
        cur.execute("SELECT * FROM users WHERE user_name = %s AND age=%s",('nico',30))
        nico_data = cur.fetchall()
        assert len(nico_data) == 1
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()
    # QUESTION: can you have two connections open at once? I open one here then open+close one in c.clear_test_db() then close one here. Does this work? 
    # QUESTION: I need a better understanding of connections and cursors

def test_newuser(client):
    """
    GIVEN a flask app
    WHEN POST submits new user information 
    THEN assert returns user_id and 200 status code
    """
    response = client.post("/newuser", data=json.dumps({"user_name":'nico',"pw":'mypw', "sex":'M',"age":30,"team":'tumbleweed',"weight":180}), content_type='application/json') 
    assert response.status_code == 200
    c.clear_test_db()

def test_log(client):
    """
    GIVEN a flask app
    WHEN POST submits user_id
    THEN assert returns all workouts for that user_id 
    """
    # populate db with user and workouts
    try:
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s,%s)",(1,'lizzkadoodle'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec,split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'PR'))
        conn.commit()
        # POST user_id and capture response
        response = client.post("/log", data=json.dumps({"user_id":1}), content_type='application/json') 
        # confirm request was successful
        assert response.status_code == 200
        # Confirm content is as expected
    finally:
        conn.close()
        cur.close()   
        # clear db
        c.clear_test_db()

def test_search_sql_str():
    """
    GIVEN an attempt to find workouts matching certain parameters
    WHEN POST submits param info to search_sql_str func 
    THEN assert returns expected string and string sub values
    """
    # Define test POST info
    search_dict = {'user_id':1,'distance':2000,'intervals':1}
    # pass search_dict to function and assert results as expected
    sql, subs = search_sql_str(search_dict)
    assert sql == "SELECT * FROM workout_log WHERE user_id=%s AND distance=%s AND intervals=%s"
    assert subs == [1,2000,1] 

def test_logsearch(client):
    """
    GIVEN a flask app
    WHEN POST sumbits workout search params 
    THEN assert expected workouts are returned + 200 status code
    """
    try: 
        # populate db with team, user, two matching workouts, two not matching
        conn, cur = db_connect('testing',False)
        cur.execute("INSERT INTO team(team_id, team_name) VALUES(1, 'UtahCrew')")
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(1,'kaja',1))
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(2,'Nico',1))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'2k PR'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(2,1,'2022-01-02', 2000,488,122,1,'2k'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(3,1,'2022-01-05', 6000,1800,130,3,'3x30min'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(4,2,'2022-01-01', 2000,484,121,1,'Nico 2k'))
        conn.commit() 
        # POST user_id and capture flask func response
        response = client.post("/logsearch", data=json.dumps({'user_id':1,'distance':2000,'intervals':1}), content_type='application/json')
        assert response.status_code == 200 
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['message']) == 2 
        # NOTE: message == [(1, 1, datetime.date(2022, 1, 1), 2000, 480, datetime.time(0, 2), datetime.time(0, 8), 1, '2k PR'), (2, 1, datetime.date(2022, 1, 2), 2000, 488, datetime.time(0, 2, 2), datetime.time(0, 8, 8), 1, '2k')]
        response = client.post("/logsearch", data=json.dumps({'user_id':1,'distance':3000,'intervals':1}), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['message']) == 0
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

def test_details(client):
    """
    GIVEN a flask app
    WHEN POST submits workout_id
    THEN assert returns interval and summary stas for that workout_id 
    """ # NOTE: not actually asserting info is correct...just that length is as expected and status_code == 200
    try: 
        # populate db: workout_log
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO workout_log(workout_id,distance,time_sec,split,intervals) VALUES(1,1000,440,110,2)")
        # populate db: interval_log
        cur.execute("INSERT INTO interval_log(workout_id,interval_type,distance,time_sec,split) VALUES(1,'distance',1000,224,112),(1,'distance',1000,216,108)")
        # POST workout_id to /details capture result
        response = client.post("/details", data=json.dumps({'workout_id':1}), content_type='application/json')
        assert response.status_code == 200
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['intervals'])==2 and len(data_dict['workout_summary'])==1
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()
    
def test_userstats(client):
    """
    GIVEN a flask app
    WHEN POST submits user_id
    THEN assert returns summary data for user
    """
    try:
        # populate db with team, user, three matching workouts, one not matching
        conn, cur = db_connect('testing',False)
        cur.execute("INSERT INTO team(team_id, team_name) VALUES(1, 'UtahCrew')")
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(1,'kaja',1))
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(2,'Nico',1))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'2k PR'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(2,1,'2022-01-02', 2000,488,122,1,'2k'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec,split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(3,1,'2022-01-05', 6000,1800,130,3,'3x30min'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split, intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(4,2,'2022-01-01', 2000,484,121,1,'Nico 2k'))
        conn.commit() 

        # pass POST to flask func
        response = client.post("/userstats", data=json.dumps({'user_id':1}), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII"))
        # check for expected results
        assert response.status_code == 200
        assert data_dict['distance'] == 22000
        assert data_dict['user_team'] == ['UtahCrew']
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

def test_add_workout():
    """
    GIVEN a POST request has been sumbitted to /addworkout 
    WHEN add_workout function is called with POST data
    THEN workout is added to workout_log table and workout_id is returned
    """
    try:
        # populate db - add user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        # pass test NewWorkout instance to function
        test_newworkout = NewWorkout(user_id=1,date='2022-06-10',distance=2000,time_sec=600,split=150,intervals=1,comment='slow 2k')
        workout_id = add_workout('testing',test_newworkout)
        # assert workout_id returned - check is int
        assert type(workout_id) == int  
    finally:
        cur.close()
        conn.close()
        c.clear_test_db() 

def test_addworkout(client):
    """
    GIVEN a flask app 
    WHEN POST with workout info submitted to /addworkout
    THEN workout is added to db and workout_id is returned
    """
    try:
        # populate db - user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        POST_dict = {'user_id':1,'date':'2022-06-14','distance':500,'time_sec':110, 'split':110, 'intervals':4,'comment':'4x500m'}
        # pass POST to flask func
        response = client.post("/addworkout", data=json.dumps(POST_dict), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII")) # status_code, workout_id
        assert response.status_code == 200
        assert type(data_dict['workout_id']) == int
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()

def test_add_interval():
    """
    GIVEN a POST request has been sumbitted to /addinterval 
    WHEN add_interval function is called with POST data
    THEN affirm True is returned indicating interval was added to interval_log table
    """
    try:
        # populate db - add user and partial workout 
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        cur.execute("INSERT INTO workout_log(workout_id) VALUES(1)")
        # create test_intervals data
        test_newinterval = NewInterval(workout_id=1,interval_type='time',distance=6000,time_sec=1800,split=130,rest=180)
        # pass test_POST data to function
        added_successfully = add_interval('testing',test_newinterval)
        # assert result
        assert added_successfully == True 
        cur.execute("SELECT distance FROM interval_log WHERE workout_id=1") 
        distance = cur.fetchone()[0]
        assert distance == 6000
    finally:
        cur.close()
        conn.close()
        c.clear_test_db() 

def test_addinterval(client):
    """
    GIVEN a flask app 
    WHEN POST with interval info submitted to /addinterval
    THEN interval is added to db and Trus is returned
    """
    try:
        # populate db - user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        cur.execute("INSERT INTO workout_log(workout_id) VALUES(1)")
        # create interval data POST
        POST_dict = {'workout_id':1,'interval_type':'time','distance':510,'time_sec':120,'split':125,'rest':60}
        # pass POST to flask func
        response = client.post("/addinterval", data=json.dumps(POST_dict), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII")) # status_code, message
        assert response.status_code == 200
        assert data_dict['message'] == True
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


# def test_():
#     """
#     GIVEN
#     WHEN
#     THEN
#     """
#     try:
#         # populate db
#         conn, cur = db_connect('testing',True)
#         sql = "INSERT INTO t(c) VALUES(%s)"
#         subs = ()
#         cur.execute(sql, subs)
#     finally:
#         cur.close()
#         conn.close()
#         c.clear_test_db() 










    
    