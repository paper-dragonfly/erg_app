import json
import yaml
import psycopg2 
from erg_app.post_classes import NewUser
import pdb 

# get database parameters
def config(db:str='erg', config_file:str='erg_app/config/config.yaml')-> dict:
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
        # add team to team table if not already in db
        cur.execute("INSERT INTO team(team_name) VALUES(%s) ON CONFLICT DO NOTHING",(resp_newuser.team,))
        #get user's team_id
        cur.execute("SELECT team_id FROM team WHERE team_name=%s",(resp_newuser.team,))
        team_id= cur.fetchone()[0]
        # add user 
        cur.execute("INSERT INTO users(user_name, age, sex, team) VALUES(%s,%s,%s,%s)",(resp_newuser.user_name, resp_newuser.age, resp_newuser.sex,team_id))
        cur.execute("SELECT user_id FROM users WHERE user_name=%s",(resp_newuser.user_name,))
        user_id = cur.fetchone()[0]
        conn.commit()
    finally: 
        conn.close()
        cur.close()
        #does this work here?
        return user_id

#Get User id
def get_user_id(user_name, db='Erg'):
    try:
        conn, cur = db_connect(db)
        cur.execute("SELECT user_id FROM users WHERE user_name=%s",(user_name,))
        user_id = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
        return user_id 

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
        


