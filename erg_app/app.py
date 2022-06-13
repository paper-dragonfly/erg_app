from flask import Flask, request 
from pydantic import ValidationError
from erg_app.post_classes import NewUser, IntervalWorkout
import json
from erg_app import logic as l
import pdb

def create_app(db):
    app = Flask(__name__) 

    @app.route("/userid",methods=["POST"]) #find user_id for existing user
    def userid():
        #POST user_name, return user_id
        user_name=request.get_json()['user_name']
        user_id = l.get_user_id(user_name, db)
        return json.dumps({'status_code':200, 'user_id': user_id})

    @app.route("/newuser", methods=['POST']) # create new user
    def newuser():
        # POST new_user info, return: user_id
        try:
            resp_newuser = NewUser.parse_obj(request.get_json())
        except ValidationError() as e:
            return json.dumps({'status_code': 400, 'message': e})
        user_id = l.add_new_user(db, resp_newuser)
        return json.dumps({'status_code': 200, 'user_id': user_id})

    @app.route("/log", methods = ['POST']) #list all workouts for user
    def log():
        # POST user_id -> all workouts listed by date for specific user. Fields: date, distance, time, av split, intervals
        try:
            user_id = request.get_json()['user_id']
            conn, cur=l.db_connect(db)
            sql = "SELECT * FROM workout_log WHERE user_id=%s ORDER BY date"
            subs = (user_id,)
            cur.execute(sql, subs)
            user_workouts =cur.fetchall() #((v1,v2,v3),(...))
        finally:
            conn.close()
            cur.close()
            return json.dumps({'status_code':200, 'message':user_workouts}, default=str) #datetime not json serializable so use defualt=str to convert non-serializable values to strings

    @app.route("/logsearch", methods = ['POST']) # returns all workouts that match search results
    def logsearch():
        workout_search_params = request.get_json()
        sql, subs = l.search_sql_str(workout_search_params)
        matching_workouts = None
        try:
            conn, cur = l.db_connect(db)
            cur.execute(sql, subs) 
            matching_workouts = cur.fetchall()
        finally:
            cur.close()
            conn.close()
            if matching_workouts == None:
                return json.dumps({'status_code':500, 'message':'error'})
            else: 
                return json.dumps({'status_code':200, 'message':matching_workouts},default=str)
            

    @app.route("/details", methods=['POST']) #list summary stats + all interval_log data for a specific workout_id
    def details():
        # POST workout_id
        workout_id = request.get_json()['workout_id']
        # List all intervals with workout_id 
        try:
            conn, cur = l.db_connect(db)
            cur.execute("SELECT * FROM interval_log WHERE workout_id=%s",(workout_id,))
            intervals = cur.fetchall()
            cur.execute("SELECT * FROM workout_log WHERE workout_id=%s",(workout_id,))
            workout_summary = cur.fetchall()
        finally:
            cur.close()
            conn.close() 
            return json.dumps({'status_code':200, 'intervals':intervals, 'workout_summary':workout_summary},default=str) 

    @app.route("/total", methods=['POST'])# display summary of all workouts for user
    def total():
        #POST user_id
        user_id = request.get_json()['user_id']
        try:
            conn,cur = l.db_connect(db)
            cur.execute("SELECT distance, time_sec FROM workout_log WHERE user_id=%s",(user_id,))
            workouts = cur.fetchall()
            dist = 0
            time = 0
            for i in range(len(workouts)):
                distance =+ workouts[i][0]
                time =+ workouts[i][1]    
        finally:
            cur.close()
            conn.close()
            return json.dumps({'status_code':200, 'distance':distance, 'time':time})

    @app.route("/teamlog", methods=['POST'])
    def teamlog():
        pass
        #return all workout descriptions (interval type, distance time num intervals) 
        # this might be hard. 
        # members = SELECT user_id FROM users WHERE team_id = x
        # SELECT * FROM workout_log WHERE user_id in members

# def boilerplate():
#     post_dict = request.get_json()
#     try:
#         conn, cur=l.db_connect(db)
#         sql = ""
#         subs = ()
#         cur.execute(sql, subs)
#         db_result=cur.fetchall()
#     finally:
#         conn.close()
#         cur.close()
#         return json.dumps({'status_code':200, 'message':None})
    
    return app 
