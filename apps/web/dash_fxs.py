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
    print('NAMES', names)
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

def post_new_interval(idict):
    return requests.post(ROOT_URL+'/addinterval',json=idict).json()

def duration_to_seconds(duration:str)->int:
    # (hh:mm:ss.d)
    if not duration:
        return 0
    hours_sec = int(duration[0:2])*60*60
    min_sec = int(duration[3:5])*60
    sec = int(duration[6:8])
    ms_sec = int(duration[9:])/100
    time_sec = (hours_sec + min_sec + sec + ms_sec)
    return time_sec

def check_duration(user_input:str)->str:
    if not user_input:
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
        return {'accept':False, 'message':'Must use correct formatting'}


def check_date(user_input:str)->str:
    print('USER INPUT ', user_input)
    if not user_input:
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

def format_time(h,m,s,t)->str: #hh:mm:ss.d
    d = {'h':h,"m":m,'s':s}
    for key in d:
        if not d[key]:
            d[key]='00'
        if len(d[key])==1:
            d[key]='0'+d[key]
        if not t:
            t='0'
    time = d['h']+":"+d['m']+":"+d['s']+":"+t
    return time

def generate_post_wo_dict(int_dict:dict, user_id:str, wo_dict:dict)->dict:
    # calculate averages 
    num_ints = len(int_dict['Date'])
    tot_time = 0
    for t in int_dict['Time']:
        t_sec = duration_to_seconds(t)
        tot_time += t_sec
    tot_dist = 0
    for d in int_dict['Distance']:
        tot_dist += d
    tot_split = 0
    for s in int_dict['Split']:
        s = '00:0'+s
        s_sec = duration_to_seconds(s)
        tot_split += s_sec
    av_split = tot_split/num_ints 
    av_sr = sum(int_dict['s/m'])/num_ints
    av_hr = sum(int_dict['HR'])/num_ints
    # populate post_dict
    wo_dict['user_id'] = int(user_id)
    wo_dict['workout_date'] = int_dict['Date'][0]
    wo_dict['time_sec']=tot_time
    wo_dict['distance']=tot_dist
    wo_dict['split']=av_split
    wo_dict['sr']=av_sr
    wo_dict['hr']=av_hr
    wo_dict['intervals']=num_ints
    wo_dict['comment']=int_dict['Comment'][0]
    return wo_dict 

def format_and_post_intervals(wo_id, i_dict):
    post_intrvl_dict_template = {'workout_id':wo_id,'time_sec':None,'distance':None,'split':None,'sr':None,'hr':None,'rest':None,'comment':None}
    for i in range(len(i_dict['Date'])):
        ipost_dict = post_intrvl_dict_template
        ipost_dict['time_sec'] = duration_to_seconds(i_dict['Time'][i])
        ipost_dict['distance'] = i_dict['Distance'][i]
        ipost_dict['split'] = duration_to_seconds("00:0"+i_dict['Split'][i])
        ipost_dict['sr'] = i_dict['s/m'][i]
        ipost_dict['hr'] = i_dict['HR'][i]
        ipost_dict['rest'] = i_dict['Rest'][i]
        ipost_dict['comment'] = i_dict['Comment'][i]
        post_new_interval(ipost_dict)    
    return

def seconds_to_duration(time_sec):
    if time_sec == 0:
        return '0'
    #seperate time into h,m,s,d
    hours = time_sec//3600
    r1 = time_sec%3600
    mins = r1//60
    r2 = r1%60
    secs = r2//1
    tenths = (r2%1)*10
    #construct duration string
    dur = ""
    for i in [hours, mins, secs,tenths]: #hh:mm:ss:dd:
        if i == 0:
            dur += '00:'
        elif 0 < i < 10:
            dur += '0'+str(i)+':'
        else:
            dur += str(i)+':'
    dur2 = dur[:8]+"."+dur[10] #hh:mm:ss.d
    #eliminate leading zeros
    zero = True
    while zero:
        for i in [0,1,3,4,6,7,9]:
            if dur2[i] != '0':
                nonz = i
                zero = False
    duration = dur2[nonz:]
    return duration 
            

   

    

    


    