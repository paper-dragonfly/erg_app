import json 
from erg_app import conftest as c
from erg_app.logic import add_new_user, db_connect, get_user_id, search_sql_str
from pydantic import BaseModel
import pdb
from erg_app.post_classes import NewUser


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
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split, duration,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,'00:02:00','00:08:00',1,'PR'))
        conn.commit()
    finally:
        conn.close()
        cur.close()   
    # POST user_id and capture response
    response = client.post("/log", data=json.dumps({"user_id":1}), content_type='application/json') 
    # confirm request was successful
    assert response.status_code == 200
    # Confirm content is as expected
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
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split, duration,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,'00:02:00','00:08:00',1,'2k PR'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split, duration,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(2,1,'2022-01-02', 2000,488,'00:02:02','00:08:08',1,'2k'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split, duration,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(3,1,'2022-01-05', 6000,1800,'00:02:10','00:30:00',3,'3x30min'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec, split, duration,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(4,2,'2022-01-01', 2000,484,'00:2:01','00:8:04',1,'Nico 2k'))
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
    try: 
        # populate db: workout_log
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO workout_log(workout_id,distance,time_sec,split,intervals) VALUES(1,1000,440,'00:01:50',2)")
        # populate db: interval_log
        cur.execute("INSERT INTO interval_log(workout_id,type,distance,time_sec,split,duration) VALUES(1,'d',1000,224,'00:01:52','00:03:44'),(1,'d',1000,216,'00:01:48','00:03:36')")
        # POST workout_id to /details capture result
        response = client.post("/details", data=json.dumps({'workout_id':1}), content_type='application/json')
        assert response.status_code == 200
        data_dict = json.loads(response.data.decode("ASCII"))
        pdb.set_trace()
        assert len(data_dict['intervals'])==2 and len(data_dict['workout_summary'])==1
    finally:
        cur.close()
        conn.close()
        c.clear_test_db()
        









    
    