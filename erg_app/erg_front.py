from importlib.resources import contents
from posixpath import split
from time import time
from turtle import distance
import requests
from typing import Dict, List, Tuple, Union
import pdb
from tabulate import tabulate

CONTENTS = """
What would you like to do? 
    1. View workout log
    2. Add workout
    3. Search by workout
    4. View your stats
    5. Exit
    """

ROOT_URL = "http://localhost:5000"

def login():
    print("Welcome to ErgTracker \n1.Login\n2.Create new account")
    resp = 0
    while resp != '1' and resp != '2':
        resp= input('pick an option using the coresponding bullet number: ')
    if resp == '1':
        print('LOGIN')
        user_name = input('User Name: ')
        # TODO: add search users feature?
        url = ROOT_URL+'/userid'
        flask_resp = requests.post(url, json={'user_name':user_name}).json()
        user_id:int = flask_resp['user_id']
    else: # resp == 2
        print('Create New User')
        user_name = input('User Name: ')
        age = int(input("Age: "))
        sex = input('Sex (M/F): ')
        team = input("Team: " )
        newuser_dict = {'user_name': user_name, "age": age, 'sex':sex, 'team': team}
        #POST newuser_dict to /newuser
        url = ROOT_URL+'/newuser'
        flask_resp = requests.post(url, json=newuser_dict).json
        user_id:int = flask_resp['user_id'] 
    return user_id, user_name

def duration_to_seconds(duration:str)->int:
    hours_sec = int(duration[0:2])*60*60
    min_sec = int(duration[3:5])*60
    sec = int(duration[6:8])
    ms_sec = int(duration[9:])/100
    time_sec = (hours_sec + min_sec + sec + ms_sec)
    return time_sec


def create_new_workout_dict(workout_type, user_id):
    date = input("Date (yyyy-mm-dd): ")
    distance = input("Distance (m): ")
    duration = input("Time (hh:mm:ss.dd): ") #TODO: how do you enforce formatting?
    time_sec = duration_to_seconds(duration)
    split_dur = input("Split (hh:mm:ss.dd): ")
    split = duration_to_seconds(split_dur)
    if workout_type > 2:
        intervals = int(input("Number of intervalse: "))
    comment = input("Comment: ")
    return({'user_id':user_id,'date':date,'distance':distance,'time_sec':time_sec, 'split':split, 'intervals':intervals,'comment':comment })

def create_intervals_dict(workout_id,interval, interval_type):
    print(f'Interval {interval}')
    distance = int(input('Distance (m): '))
    time_sec = duration_to_seconds(input('Time (hh:mm:ss.dd): '))
    split = duration_to_seconds(input('Split (hh:mm:ss.dd): '))
    rest =  duration_to_seconds(input('Rest (hh:mm:ss.dd): '))
    return {'workout_id':workout_id,'interval_type':interval_type,'distance':distance,'time_sec':time_sec,'split':split,'rest':rest}          

def run(): # TODO: how do I write tests for things with user input? 
    user_id, user_name = login()
    action = 0
    while int(action) != 5: # not Exit
        print(CONTENTS)
        try: 
            action = int(input('Choose the number corresponding to your desired action: '))
        except ValueError:
            print('must be number, app exited')
            action = 5 

        if action == 1: # view workout log
            url = ROOT_URL+'/log'
            workout_log:list = requests.post(url, json={'user_id':user_id}).json()['message'] #[(...)(...)]
            # if no workouts
            if len(workout_log) == 0:
                print('No workouts for this user')
            else: 
                #display as table
                workout_log.insert(0,["workout_id","user_id","date","distance","time_sec","split","duration","intervals","comment"])
                print(f'Workout Log for {user_name}')
                print(tabulate(workout_log, headers='firstrow'))

        elif action == 2: # add workout
            print('Select Workout:\n\t1.Single Time\n\t2.Single Distance\n\t3.Interval Time\n\t4.Interval Distance') # TODO add inverval variable for more complexity
            valid_selection = False
            # get user to choose workout type
            while not valid_selection:
                try:
                    workout_type = int(input('Choose corresponding number: ' ))
                    if workout_type in range(1,5):
                        valid_selection = True
                except ValueError:
                    print('ValueError, must choose integer')
            # get POST data
            post_data = create_new_workout_dict(workout_type, user_id)
            # Add Workout: send POST to /addworkout to add workout to workout_log 
            url=ROOT_URL+'/addworkout'
            flask_resp = requests.post(url, json=post_data).json() #Status_code, workout_id 
            # Is it an interval workout?
            interval_count = post_data['intervals']
            if interval_count>1:
                # get type of interval workout
                interval_type = input('Workout type (Distance/Time): ')
                if interval_type[0].lower == 'd':
                    interval_type = 'distance'
                else:
                    interval_type = 'time'
                workout_id = flask_resp['workout_id']
                interval = 1
                while interval <= interval_count:
                    # get POST data 
                    post_data_intervals = create_intervals_dict(workout_id, interval, interval_type)
                    # Add Interval: sent POST to /addinterval to add interval to interval_log
                    url=ROOT_URL+'/addinterval'
                    flask_resp = requests.post(url, json=post_data_intervals).json()
                    interval += 1 

        elif action == 3: # search by workout
            pass
        elif action == 4: # view user_stats
            pass
        else:
            print('Invalid Entry, try again')

    return  

if __name__ == "__main__":
    run()