import requests
import json
import re
from constants import ROOT_URL
import pdb 


def flask_requests_post(url:str,data:dict,):
    return requests.post(url, json=data).json()


def flask_requests_get(url:str):
    return requests.get(url).json()


def flask_client_post(url:str, data:dict,client):
    response = client.post(url, data=json.dumps(data), content_type='application/json')
    return json.loads(response.data.decode("ASCII"))


def flask_client_get(url:str,client):
    response = client.get(url)
    return json.loads(response.data.decode("ASCII"))

def get_usernames():
    names = requests.get(ROOT_URL+'/usernames').json()['user_names']
    name_list = []
    for i in range(len(names)):
        name_list.append(names[i][0].capitalize())
    return name_list

def get_id(user_name):
    return requests.get(ROOT_URL+f'/userid/{user_name}').json()['user_id']

def get_name(id):
    name = requests.get(ROOT_URL+f'/username/{id}').json()['user_name']
    return name

def post_new_workout(wdict):
    return requests.post(ROOT_URL+'/addworkout',json=wdict).json()

def duration_to_seconds(duration:str)->int:
    # (hh:mm:ss.d)
    hours_sec = int(duration[0:2])*60*60
    min_sec = int(duration[3:5])*60
    sec = int(duration[6:8])
    ms_sec = int(duration[9:])/100
    time_sec = (hours_sec + min_sec + sec + ms_sec)
    return time_sec

def input_duration(user_input:str)->str:
    if user_input == "":
        return {'accept':True, 'message':user_input}
    #hh:mm:ss[.d]
    # if formatting correct
    f = re.findall('[0-2]\d:[0-5]\d:[0-5]\d', user_input)
    if len(f) == 1:
        # if hours in range
        if int(user_input[0:2])<24:
            # add ms if neccessary
            if len(user_input) == 8:
                user_input += '.0'
                return {'accept':True, 'message':user_input}
            # if input includes ms
            elif len(user_input) == 10:
                #if ms formatting correct
                if re.findall('.\d$', user_input):
                    return {'accept':True, 'message':user_input}
                else:
                    return {'accept':False, 'message':'ms formatting incorrect'}
            else:
                return {'accept':False, 'message':'input length incorrect'}
        else:
            return {'accept':False, 'message':'hours out of range'}
    else:
        return {'accept':False, 'message':'Must use hh:mm:ss.d formatting'}


def input_date(user_input:str)->str:
    print('USER INPUT ', user_input)
    if user_input == "":
        return {'accept': True, 'message': user_input}
    #yyyy-mm-dd 
    # if input matches formatting
    if len(re.findall('\d\d\d\d-[0-1]\d-[0-3]\d', user_input)) == 1:
        print('FORMATTING CORRECT')
        # if month a real month 
        if 0<int(user_input[5:7])<=12:
            # if month has 31 days
            if user_input[5:7] in ['01','03','05','07','08','10','12']:
                #if day valid
                if 0<int(user_input[8:10])<=31:
                    return {'accept':True, 'message':user_input}
                else:
                    return {'accept':False, 'message':"day out of range"}
            #if month has 30 days
            elif user_input[5:7] in ['04','06','09','11']:
                #if day valid
                if 0<int(user_input[8:10])<=30:
                    return {'accept':True, 'message':user_input}
                else:
                    return {'accept':False, 'message':"day out of range"}
            # if febuary
            elif user_input[5:7] == '02':
                #if day valid
                if 0<int(user_input[8:10])<=28:
                    return {'accept':True, 'message':user_input}
                else:
                    return {'accept':False, 'message':"day out of range"}
        # month not real month
        else:
            return {'accept':False, 'message':"month out of range"}
    else: 
        print('FORMATTING BAD')
        return {'accept':False, 'message':"Must use yyyy-mm-dd formatting"}
    