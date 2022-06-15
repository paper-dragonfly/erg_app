from importlib.resources import contents
from posixpath import split
from time import time
from turtle import distance
import requests
from typing import Dict, List, Tuple, Union
import pdb
from tabulate import tabulate
import re

CONTENTS = """
What would you like to do? 
    1. View workout log
    2. Add workout
    3. Search by workout
    4. View your stats
    5. Exit
    """

ROOT_URL = "http://localhost:5000"

def login()->tuple:
    print("\nWelcome to ErgTracker \n1.Login\n2.Create new account")
    resp = 0
    while resp != '1' and resp != '2': # while invalid entry
        resp= input('pick an option using the coresponding bullet number: ')
    if resp == '1': # Login
        valid_input = False # Question: is this the way to ensure valid entries that don't break the program?
        while valid_input == False:
            print('\nLOGIN')
            print('1. List Users \n2. Search by User Name')
            user_choice = input('> ')
            try:
                if int(user_choice) == 1: # List users
                    # get user names
                    url = ROOT_URL+'/usernames'
                    flask_user_names = requests.get(url).json()['user_names']
                    # print user names
                    print('\nUser Names') 
                    for i in range(len(flask_user_names)):
                        print(flask_user_names[i][0])
                # Select user by user_name 
                user_name = input('\nUser Name: ') 
                url = ROOT_URL+'/userid'
                flask_resp = requests.post(url, json={'user_name':user_name}).json()
                user_id:int = flask_resp['user_id']
                valid_input = True
            except ValueError:
                print('ValueError: must select 1 or 2')
    else: # resp == 2 Create new account
        print('\nCreate New User')
        user_name = input('User Name: ')
        v = False
        while not v:
            try: 
                age = int(input("Age: "))
                v = True
            except ValueError:
                print('Age must be an integer')
        v = False
        sex = ''
        while sex != 'M' and sex != 'F':    
            sex = input('Sex (M/F): ').upper()
            if sex != 'M' and sex != 'F':
                print('Must select M or F')
        team = input("Team: " )
        newuser_dict = {'user_name': user_name, "age": age, 'sex':sex, 'team': team}
        #POST newuser_dict to /newuser
        url = ROOT_URL+'/newuser'
        flask_resp = requests.post(url, json=newuser_dict).json()
        user_id:int = flask_resp['user_id'] 
        print(f'\nNew user created. Welcome {user_name}')
    return user_id, user_name

def duration_to_seconds(duration:str)->int:
    hours_sec = int(duration[0:2])*60*60
    min_sec = int(duration[3:5])*60
    sec = int(duration[6:8])
    ms_sec = int(duration[9:])/100
    time_sec = (hours_sec + min_sec + sec + ms_sec)
    return time_sec

def input_int(prompt_str:str):
    user_input = input(prompt_str)
    if user_input == "":
        return user_input
    valid = False
    while not valid:
        try:
            user_input = int(input(prompt_str))
            valid = True
        except ValueError:
            print('Input must be integer')
    return user_input

def input_duration(prompt_str):
    user_input = input(prompt_str)
    if user_input == "":
        return user_input
    #hh:mm:ss.dd
    while len(re.findall('[0-2]\d:[0-5]\d:[0-5]\d.\d\d',user_input)) != 1:
        print('Must use hh:mm:ss.dd formatting')
        user_input = input(prompt_str)
    while int(user_input[0-2])>23: 
        print('Must use hh:mm:ss.dd formatting')
        user_input = input(prompt_str)
    return user_input 

def input_date(prompt_str):
    user_input = input(prompt_str)
    if user_input == "":
        return user_input
    #yyyy-mm-dd
    v = False # Question: v never becomes True but it seems to be doing its job...is this the right way to do this?
    while not v: 
        # if input matches formatting
        if len(re.findall('\d\d\d\d-[0-1]\d-[0-3]\d', user_input)) == 1:
            # if month a real month 
            if 0<int(user_input[5:7])<=12:
                # if month has 31 days
                if user_input[5:7] in ['01','03','05','07','08','10','12']:
                    #if day valid
                    if 0<int(user_input[8:10])<=31:
                        return user_input
                    else:
                        print("day out of range")
                #if month has 30 days
                elif user_input[5:7] in ['04','06','09','11']:
                    #if day valid
                    if 0<int(user_input[8:10])<=30:
                        return user_input
                    else:
                        print("day out of range")
                # if febuary
                elif user_input[5:7] == '02':
                    #if day valid
                    if 0<int(user_input[8:10])<=28:
                        return user_input
                    else:
                        print('day out of range')
            # month not real month
            else:
                print('month out of range')
        else: 
            print('Must use yyyy-mm-dd formatting')
        user_input = input("Date (yyyy-mm-dd): ")

def create_new_workout_dict(workout_type, user_id):
    date = input("Date (yyyy-mm-dd): ") 
    while len(re.findall('\d\d\d\d-0*[0-12]-0*[0-31]', date)) != 1 and date!="":
        print('Must use yyyy-mm-dd formatting')
        date = input("Date (yyyy-mm-dd): ")              
    v_dist = False # Question: best way to validate formatting? Is there a better way
    distance = input_int('Distance (m): ')
    duration = input("Time (hh:mm:ss.dd): ") #TODO: how do you enforce formatting?
    time_sec = duration_to_seconds(duration)
    split_dur = input("Split (hh:mm:ss.dd): ")
    split = duration_to_seconds(split_dur)
    if workout_type > 2:
        intervals = int(input("Number of intervalse: "))
    else:
        intervals = 1
    comment = input("Comment: ")
    return({'user_id':user_id,'date':date,'distance':distance,'time_sec':time_sec, 'split':split, 'intervals':intervals,'comment':comment })

def create_intervals_dict(workout_id,interval, interval_type):
    print(f'Interval {interval}')
    distance = int(input('Distance (m): '))
    time_sec = duration_to_seconds(input('Time (hh:mm:ss.dd): '))
    split = duration_to_seconds(input('Split (hh:mm:ss.dd): '))
    rest =  duration_to_seconds(input('Rest (hh:mm:ss.dd): '))
    return {'workout_id':workout_id,'interval_type':interval_type,'distance':distance,'time_sec':time_sec,'split':split,'rest':rest}          

def create_logsearch_dict():
    print('Search by different parameters, press enter to skip a param')
    data_dict = {}
    # get user input data for search params
    valid_entry = False
    while valid_entry == False:
        try: 
            date = input('Date (yyyy-mm-dd): ')
            distance = input('Distance (m): ')
            # if user skips distance
            if distance == "":
                distance = 0
            # if distance value given
            else:
                distance = int(distance)
            # request user_input time
            time_raw = input('Time (hh:mm:ss):' )
            # if time skipped
            if time_raw == "":
                time = 0
            # convert str time to time in seconds
            else: 
                time = time_raw+'.00'
                time = duration_to_seconds(time)
            # request user_input intervals
            intervals = input('Number of Intervals: ')
            # if intervals skipped
            if intervals == "":
                intervals = 0
            else:
                intervals = int(intervals) 
            valid_entry = True
        except ValueError: #user_input not int where int is required
            print('distance and intervals must be integers')
    raw_data_dict = {'date':date,'distance':distance,'time_sec':time,'intervals':intervals}
    # exclude skipped params
    for key in raw_data_dict:
        if raw_data_dict[key] != "" and raw_data_dict[key] != 0:
            data_dict[key] = raw_data_dict[key]
    return data_dict

def run(): # TODO: how do I write tests for things with user input? 
    user_id, user_name = login()
    action = 0
    while int(action) != 5: # not Exit
        print(CONTENTS)
        try: 
            action = int(input('Choose the number corresponding to your desired action: '))
        except ValueError:
            pass 
        if action == 1: # view workout log
            print('\n')
            url = ROOT_URL+'/log'
            workout_log:list = requests.post(url, json={'user_id':user_id}).json()['message'] #[[...],[...]]
            # if no workouts
            if len(workout_log) == 0:
                print('No workouts for this user')
            else: 
                #display as table
                workout_log.insert(0,["workout_id","user_id","date","distance","time_sec","split","intervals","comment"])
                print(f'Workout Log for {user_name}')
                print(tabulate(workout_log, headers='firstrow'))

        elif action == 2: # add workout
            print('\n')
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
            print('\n')
            post_data:dict = create_logsearch_dict()
            url = ROOT_URL+'/logsearch'
            flask_select_workouts:list = requests.post(url, json=post_data).json()['message'] #[[...][...]]
            # if no workouts
            if len(flask_select_workouts) == 0:
                print('No workouts for this search')
            else: 
                #display as table
                flask_select_workouts.insert(0,["workout_id","user_id","date","distance","time_sec","split","intervals","comment"])
                print(f'\nSearch Results')
                print(tabulate(flask_select_workouts, headers='firstrow'))

        elif action == 4: # view user_stats
            print('\n')
            url = ROOT_URL+'/userstats'
            flask_userstats:dict = requests.post(url, json={'user_id':user_id}).json()
            user_info = [['User Name', 'Age', 'Sex', 'Team'],[flask_userstats['user_info'][1],flask_userstats['user_info'][2],flask_userstats['user_info'][3], flask_userstats['user_team']]]
            print(tabulate(user_info, headers='firstrow'))
            print('\n')
            userstats_list = [["Total Distance","Total Time", "Total Number of Workouts"],[flask_userstats['distance'],flask_userstats['time'],flask_userstats['count']]]
            print(tabulate(userstats_list, headers='firstrow'))
        elif action == 5: # Exit
            print('\nGame Exited')
        else:
            print('Invalid Entry, try again')

    return  

if __name__ == "__main__":
    run()