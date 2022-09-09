import json
import yaml
import psycopg2 
from apps.api.post_classes import NewInterval, NewUser, NewWorkout
import pdb 

# get database parameters
def config(db:str='erg', config_file:str='apps/api/config/config.yaml')-> dict:
    with open(f'{config_file}', 'r') as f:
        config_dict = yaml.safe_load(f) 
    db_params = config_dict[db]
    return db_params 


# connect to database
def db_connect(db:str, autocommit:bool = False):
    params = config(db)
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    conn.autocommit = autocommit
    return conn, cur


# add new user to db
def add_new_user(db:str, resp_newuser:NewUser)->int:
    user_id = 0
    try:
        conn, cur = db_connect(db)
        #check if user already exists
        cur.execute('SELECT user_name FROM users')
        usernames = cur.fetchall()
        for i in range(len(usernames)):
            if usernames[i][0] == resp_newuser.user_name: 
                return 0
        # add team to team table if not already in db
        cur.execute("INSERT INTO team(team_name) VALUES(%s) ON CONFLICT DO NOTHING",(resp_newuser.team,))
        #get user's team_id
        cur.execute("SELECT team_id FROM team WHERE team_name=%s",(resp_newuser.team,))
        team_id= cur.fetchone()[0]
        # add user 
        cur.execute("INSERT INTO users(user_name, dob, sex, team) VALUES(%s,%s,%s,%s)",(resp_newuser.user_name, resp_newuser.dob, resp_newuser.sex,team_id))
        cur.execute("SELECT user_id FROM users WHERE user_name=%s",(resp_newuser.user_name,))
        user_id = cur.fetchone()[0]
        conn.commit()
    finally: 
        conn.close()
        cur.close()
        return user_id


#Get user_name from ID
def get_user_name(id, db):
    try:
        conn, cur = db_connect(db)
        cur.execute("SELECT user_name FROM users WHERE user_id=%s",(id,))
        user_name = cur.fetchone()[0]
    # exception - no user_name maches given user_name
    except:  
        user_name = 'No Match'
    finally:
        cur.close()
        conn.close()
        return user_name 


#Get User id
def get_user_id(user_name, db='Erg'):
    try:
        conn, cur = db_connect(db)
        cur.execute("SELECT user_id FROM users WHERE user_name=%s",(user_name,))
        user_id = cur.fetchone()[0]
    # exception - no user_name maches given user_name
    except:  
        user_id = 0
    finally:
        cur.close()
        conn.close()
        return user_id 


# add workout to workout_log
def add_workout(db:str, workout_inst:NewWorkout)->int:
    try:
        # connect to db
        conn, cur = db_connect(db, True)
        # add workout data to workout_log table
        sql = "INSERT INTO workout_log(user_id, workout_date, distance, time_sec, split, sr, hr, intervals, comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        subs = (workout_inst.user_id, workout_inst.workout_date, workout_inst.distance, workout_inst.time_sec, workout_inst.split, workout_inst.sr, workout_inst.hr, workout_inst.intervals, workout_inst.comment) 
        cur.execute(sql, subs)
        cur.execute("SELECT MAX(workout_id) from workout_log")
        workout_id = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
        return workout_id  


# add interval to interval_log 
def add_interval(db:str, interval_inst:NewInterval)->bool:
    added = False
    try:
        # connect to db
        conn, cur = db_connect(db, True)
        # add interval data to interval_log table
        sql = "INSERT INTO interval_log(workout_id, time_sec, distance, split, sr, hr, rest, comment, intrvl_wo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        subs = (interval_inst.workout_id, interval_inst.time_sec, interval_inst.distance, interval_inst.split, interval_inst.sr, interval_inst.hr, interval_inst.rest, interval_inst.comment, interval_inst.intrvl_wo) 
        cur.execute(sql, subs)
        added = True
    finally:
        cur.close()
        conn.close()
        return added  


def search_sql_str(workout_search_params:dict)-> str:
    sql = 'SELECT * FROM workout_log WHERE '
    subs = []
    l = len(workout_search_params) 
    i = 1
    for key in workout_search_params:
        if i < l:
            sql+= key
            sql+= '=%s AND '
            subs.append(workout_search_params[key])
        else:
            sql+= key
            sql+= '=%s'
            subs.append(workout_search_params[key])
        i += 1
    return sql, subs 
        


