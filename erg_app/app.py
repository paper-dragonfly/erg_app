from flask import Flask, request 
from pydantic import ValidationError 
from erg_app.post_classes import NewInterval, NewUser, NewWorkout
import json
from erg_app import logic as l
import pdb

def create_app(db):
    app = Flask(__name__) 

    #TODO: new as of Aug 19, no tests yet
    @app.route('/username/<id>', methods=['GET'])
    def get_username(id):
        user_name = l.get_user_name(id, db)
        return json.dumps({'status_code': 200, 'user_name': user_name})

    @app.route("/userid/<user_name>",methods=["GET"]) #find user_id for existing user
    def userid(user_name):
        #Submit user_name, return user_id
        user_id = l.get_user_id(user_name, db)
        return json.dumps({'status_code':200, 'user_id': user_id})
    

    @app.route("/usernames", methods = ['GET'])
    def usernames():
        # GET, return all user_names 
        user_names = []
        try: 
            conn, cur = l.db_connect(db)
            cur.execute('SELECT user_name FROM users')
            user_names = cur.fetchall() #[["n1"],["n2"]]
        finally: 
            cur.close()
            conn.close()
            return json.dumps({'status_code': 200, 'user_names': user_names})


    @app.route("/newuser", methods=['POST']) # create new user
    def newuser():
        # POST new_user info, return: user_id
        try:
            resp_newuser = NewUser.parse_obj(request.get_json())
        except ValidationError() as e:
            return json.dumps({'status_code': 400, 'message': e})
        user_id = l.add_new_user(db, resp_newuser)
        return json.dumps({'status_code': 200, 'user_id': user_id})


    @app.route("/log/<user_id>", methods = ['GET']) #list all workouts for user
    def log(user_id):
        # submit GET request with user_id -> all workouts listed by date for specific user. Fields: date, distance, time, av split, intervals
        try:
            conn, cur=l.db_connect(db)
            user_id = int(user_id)
            sql = "SELECT * FROM workout_log WHERE user_id=%s ORDER BY date"
            subs = (user_id,)
            cur.execute(sql, subs)
            user_workouts = cur.fetchall() #[(v1,v2,v3),(...)]
        except ValueError:
            return json.dumps({'status_code':400, 'message':'user_id must be integer'})
        finally:
            conn.close()
            cur.close()
            return json.dumps({'status_code':200, 'message':user_workouts}, default=str) #datetime not json serializable so use defualt=str to convert non-serializable values to strings


    @app.route('/addworkout', methods=['POST'])
    def addworkout():
        # POST user_id, date, distance, time_sec, split, intervals, comment | return: workout_id
        try:
            workout_inst = NewWorkout.parse_obj(request.get_json())
        except ValidationError() as e:
            return json.dumps({'status_code': 400, 'message': e})
        workout_id = l.add_workout(db, workout_inst)
        return json.dumps({'status_code': 200, 'workout_id': workout_id})


    @app.route('/addinterval', methods=['POST'])
    def addinterval():
        #POST workout_id, interval_type, distance, time_sec, split, rest
        try:
            interval_inst = NewInterval.parse_obj(request.get_json())
        except ValidationError() as e:
            return json.dumps({'status_code': 400, 'message': e})
        add_successful:bool = l.add_interval(db, interval_inst) 
        return json.dumps({'status_code': 200, 'message':add_successful})    


    @app.route("/logsearch", methods = ['GET']) # returns all workouts that match search results
    def logsearch():
        workout_search_params:dict = request.args 
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
                return json.dumps({'status_code':500, 'message':[]})
            else: 
                return json.dumps({'status_code':200, 'message':matching_workouts},default=str)
            

    @app.route("/details", methods=['GET']) #list summary stats + all interval_log data for a specific workout_id
    def details():
        # retrieve workout_id
        workout_id = request.args["workout_id"]
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


    @app.route("/userstats", methods=['GET'])# display summary of all workouts for user
    def total():
        #POST user_id | return status_code, total_distance, total_time, total_workouts, user_info fm users, user's team
        user_id = request.args['user_id']
        try:
            conn,cur = l.db_connect(db)
            cur.execute("SELECT * FROM users WHERE user_id=%s",(user_id,))
            user_info = cur.fetchone()
            cur.execute("SELECT team_name FROM team WHERE team_id=(SELECT team FROM users WHERE user_id=%s)",(user_id,))
            user_team = cur.fetchone()
            cur.execute("SELECT distance, time_sec, intervals FROM workout_log WHERE user_id=%s",(user_id,))
            workouts = cur.fetchall()
            distance = 0
            time = 0
            count = len(workouts)
            # calculate total distance and time
            for i in range(len(workouts)):
                distance += (workouts[i][0])
                time += workouts[i][1]    
        finally:
            cur.close()
            conn.close()
            return json.dumps({'status_code':200, 'distance':distance, 'time':time, 'count':count, "user_info": user_info, "user_team":user_team})


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

if __name__ == '__main__':
    app = create_app('erg')
    app.run(host='localhost', port=5000, debug=True)
