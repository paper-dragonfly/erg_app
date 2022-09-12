import json 
from apps.api import conftest as c
from apps.api.logic import add_new_user, db_connect, get_user_id, search_sql_str, add_workout, add_interval, get_users
from pydantic import BaseModel
import pdb
from apps.api.post_classes import NewUser, NewInterval, NewWorkout


def test_01_users(client):
    """
    GIVEN a flask app
    WHEN a GET request is submitted to /users
    THEN assert return dict includes body key with all user info
    """
    try:
        #populate db with two users
        conn, cur= db_connect('testing', True)
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
        # mak
        # send GET request for user_id 
        response = client.get("/users")
        assert response.status_code == 200        
        data_dict = json.loads(response.data.decode("ASCII"))
        assert data_dict['body']['user_name'] == ['kaja','moonshine']
    finally:
        c.clear_test_db
        cur.close()
        conn.close()


def test_get_user_id():
    """
    GIVEN a user_name
    WHEN user_name and db_name are passed to get_user_id() 
    THEN assert expected user_id is returned
    """
    conn, cur = db_connect('testing', True)
    try: 
        # populate db with user if not exists
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(1,'kaja'))
        # use f(x) to get id
        assert get_user_id('kaja', 'testing') == 1
        assert get_user_id('not_real', 'testing') == 0
    finally: 
        c.clear_test_db()
        cur.close()
        conn.close()


def test_userid(client):
    """
    GIVEN a flask app 
    WHEN GET submits a user_name
    THEN assert that the returned user_id is as expected
    """
    try: 
        #populate db with user 
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(1,'kaja'))
        # send GET request for user_id 
        response = client.get("/userid/kaja")
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
    test_user = NewUser(user_name='nico', dob='1991-12-01', sex='Male',team='tumbleweed')
    #pass to add_new_user()
    user_id = add_new_user('testing',test_user)
    # get test_user data from db 
    try: 
        conn, cur = db_connect('testing')
        cur.execute("SELECT * FROM users WHERE user_name = %s",('nico',))
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
    response = client.post("/newuser", data=json.dumps({"user_name":'nico', "dob":"1991-12-01", "sex":'Male',"team":'tumbleweed'}), content_type='application/json') 
    assert response.status_code == 200
    c.clear_test_db()


def test_log(client):
    """
    GIVEN a flask app
    WHEN GET submits user_id
    THEN assert returns all workouts for that user_id 
    """
    # populate db with user and workouts
    try:
        conn, cur = db_connect('testing',True)
        # add user
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s,%s)",(1,'lizzkadoodle'))
        # add workout
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec,split,sr,hr,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,30,155,1,'PR'))
        conn.commit()
        # send GET request with user_id to /log and capture response
        response = client.get("/log/1") 
        # confirm request was successful
        assert response.status_code == 200
        # Confirm content is as expected
        assert 'PR' in response.data.decode("ASCII")
    finally:
        conn.close()
        cur.close()   
        # clear db
        c.clear_test_db()


def test_search_sql_str():
    """
    GIVEN an attempt to find workouts matching certain parameters
    WHEN GET submits param info to search_sql_str func 
    THEN assert returns expected string and string sub values
    """
    # Define test GET url info
    search_dict = {'user_id':1,'distance':2000,'intervals':1}
    # pass search_dict to function and assert results as expected
    sql, subs = search_sql_str(search_dict)
    assert sql == "SELECT * FROM workout_log WHERE user_id=%s AND distance=%s AND intervals=%s"
    assert subs == [1,2000,1] 


def test_logsearch(client):
    """
    GIVEN a flask app
    WHEN GET sumbits workout search params 
    THEN assert expected workouts are returned + 200 status code
    """
    try: 
        # populate db with team, user, two matching workouts, two not matching
        conn, cur = db_connect('testing',False)
        cur.execute("INSERT INTO team(team_id, team_name) VALUES(1, 'UtahCrew')")
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(1,'kaja',1))
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(2,'Nico',1))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'2k PR'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(2,1,'2022-01-02', 2000,488,122,1,'2k'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(3,1,'2022-01-05', 6000,1800,130,3,'3x30min'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(4,2,'2022-01-01', 2000,484,121,1,'Nico 2k'))
        conn.commit() 

        # GET user_id and capture flask func response
        response = client.get("/logsearch?user_id=1&distance=2000&intervals=1")
        assert response.status_code == 200 
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['message']) == 2 
        # NOTE: message == [(1, 1, datetime.date(2022, 1, 1), 2000, 480, datetime.time(0, 2), datetime.time(0, 8), 1, '2k PR'), (2, 1, datetime.date(2022, 1, 2), 2000, 488, datetime.time(0, 2, 2), datetime.time(0, 8, 8), 1, '2k')]
        response = client.get("/logsearch?user_id=1&distance=3000&intervals=1")
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['message']) == 0
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_details(client):
    """
    GIVEN a flask app
    WHEN GET submits workout_id
    THEN assert returns interval and summary stas for that workout_id 
    """ # NOTE: not actually asserting info is correct...just that length is as expected and status_code == 200
    try: 
        # populate db: workout_log
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO workout_log(workout_id,distance,time_sec,split,intervals) VALUES(1,1000,440,110,2)")
        # populate db: interval_log
        cur.execute("INSERT INTO interval_log(workout_id,intrvl_wo,distance,time_sec,split) VALUES(1,True,1000,224,112),(1,True,1000,216,108)")
        # sent GET requ with workout_id to /details capture result
        response = client.get("/details?workout_id=1")
        assert response.status_code == 200
        data_dict = json.loads(response.data.decode("ASCII"))
        assert len(data_dict['intervals'])==2 and len(data_dict['workout_summary'])==10 #num cols in wo_log
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()


def test_userstats(client):
    """
    GIVEN a flask app
    WHEN GET request submits user_id
    THEN assert returns summary data for user
    """
    try:
        # populate db with team, user, three matching workouts, one not matching
        conn, cur = db_connect('testing',False)
        cur.execute("INSERT INTO team(team_id, team_name) VALUES(1, 'UtahCrew')")
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(1,'kaja',1))
        cur.execute("INSERT INTO users(user_id, user_name, team) VALUES(%s,%s,%s)",(2,'Nico',1))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'2k PR'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(2,1,'2022-01-02', 2000,488,122,1,'2k'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec,split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(3,1,'2022-01-05', 18000,1800,130,3,'3x30min'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, distance, time_sec, split, intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(4,2,'2022-01-01', 2000,484,121,1,'Nico 2k'))
        conn.commit() 

        # pass GET to flask func
        response = client.get("/userstats?user_id=1")
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
        test_newinterval = NewInterval(workout_id=1,intrvl_wo=True, distance=6000,time_sec=1800,split=130,rest=180)
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
    THEN interval is added to db and True is returned
    """
    try:
        # populate db - user
        conn, cur = db_connect('testing',True)
        sql = "INSERT INTO users(user_id, user_name) VALUES(%s,%s)"
        subs = (1,'sam')
        cur.execute(sql, subs)
        cur.execute("INSERT INTO workout_log(workout_id) VALUES(1)")
        # create interval data POST
        POST_dict = {'workout_id':1,'intrvl_wo':'True','distance':510,'time_sec':120,'split':125,'rest':60}
        # pass POST to flask func
        response = client.post("/addinterval", data=json.dumps(POST_dict), content_type='application/json')
        data_dict = json.loads(response.data.decode("ASCII")) # status_code, message
        assert response.status_code == 200
        assert data_dict['message'] == True
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()










    
    