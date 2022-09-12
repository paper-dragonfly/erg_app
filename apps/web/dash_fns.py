import requests
import json
import re
from apps.web.constants import ROOT_URL
import pdb 

# FLASK get+post for requests/client
def flask_requests_get(url:str):
    return requests.get(url).json()


def flask_requests_post(url:str,data:dict,):
    return requests.post(url, json=data).json()


def flask_client_get(url:str,client):
    response = client.get(url)
    return json.loads(response.data.decode("ASCII"))


def flask_client_post(url:str, data:dict,client):
    response = client.post(url, data=json.dumps(data), content_type='application/json')
    return json.loads(response.data.decode("ASCII"))

# GET requests
def get_usernames(get=flask_requests_get, get_args={}):
    names:tuple = get(ROOT_URL+'/users', **get_args)['body']['user_name']
    name_list = []
    for i in range(len(names)):
        name_list.append(names[i].capitalize())
    return name_list


def get_id(user_name, get=flask_requests_get, get_args={}):
    flask_resp_users = get(ROOT_URL+f'/users', **get_args)['body']
    idx = flask_resp_users['user_name'].index(user_name)
    user_id = flask_resp_users['user_id'][idx]
    return user_id 
    

def get_name(id, get=flask_requests_get, get_args={}):
    flask_resp_users = get(ROOT_URL+f'/users', **get_args)['body']
    idx = flask_resp_users['user_id'].index(id)
    user_name = flask_resp_users['user_name'][idx]
    return user_name


def get_wo_details(wo_id, get=flask_requests_get, get_args={}):
    return get(ROOT_URL+f'/details?workout_id={wo_id}',**get_args)

# POST requests
def post_newuser(newuser_dict, post=flask_requests_post, post_args={}):
    return post(ROOT_URL+'/newuser',newuser_dict,**post_args)

def post_new_workout(wdict, post=flask_requests_post, post_args={}):
    return post(ROOT_URL+'/addworkout',wdict, **post_args)

def post_new_interval(idict, post=flask_requests_post, post_args={}):
    return post(ROOT_URL+'/addinterval',idict,**post_args)


# Check Formatting 
def check_date(input_date:str)->dict: #'Jan 01 2000' -> yyyy-mm-dd
    if not input_date: #allow empty submission
        return {'success':True, 'message': ""}
    reformat_result = reformat_date(input_date)
    if not reformat_result['success']:
        return reformat_result #keys: success , message
    date = reformat_result['message']
    # if month has 31 days
    if date[5:7] in ['01','03','05','07','08','10','12']:
        #if day valid
        if 0<int(date[8:10])<=31:
            return {'success':True, 'message':date}
        else:
            return {'success':False, 'message':"Date formatting error: day out of range"}
    #if month has 30 days
    elif date[5:7] in ['04','06','09','11']:
        #if day valid
        if 0<int(date[8:10])<=30:
            return {'accept':True, 'message':date}
        else:
            return {'accept':False, 'message':"Date formatting error: day out of range"}
    # if febuary
    elif date[5:7] == '02':
        #if day valid
        if 0<int(date[8:10])<=28:
            return {'accept':True, 'message':date}
        else:
            return {'accept':False, 'message':"Date formatting error: day out of range"}


def check_duration(input_dur:str, d_type='Time')->dict: 
    if not input_dur: #allow empty submission 
        return {'accept':True, 'message':input_dur}
    # adjust input_time to full format length
    blank = '00:00:00.0'
    short = 10 - len(time)
    time = blank[:short]+time
    correct = 'hh:mm:ss.d'
    if d_type == 'Split':
       correct = 'm:ss.d' 
    # check if formatting correct
    f = re.findall('^([0-1]\d|[2][0-4]):[0-5]\d:[0-5]\d[.]\d$', input_dur)
    if len(f) != 1:
        return {'success':False, 'message':f'{d_type} formatting error: must use {correct} formatting'}
    return {'accept':True, 'message':input_dur}    


def check_sr_formatting(stroke_rate):
    if len(re.findall('^\d*\d$', stroke_rate)) != 1:
        return {'success':False, "message":'Stroke rate formatting error: must be integer'}
    return {'success':True, "message":stroke_rate}


def check_dist_formatting(dist):
    if len(re.findall('^\d+$', dist)):
        return {'success':True, 'message':dist}
    return {'success':False, 'message':'Distance formatting error'}


def check_hr_formatting(hr):
    if hr == 'n/a' or len(re.findall('^\d+$',hr)) == 1 or hr == "":
        return {'success':True, 'message':hr}
    return {'success':False, 'message':'Heart rate formatting error'}


def check_rest_formatting(rest):
    if rest == "n/a" or rest == "" or len(re.findall('^\d+$', rest)):
        return {'success':True, 'message':rest}
    return {'success':False, 'message':'Rest formatting error'}


def validate_form_inputs(date, time, dist, split, sr, hr, rest):
    valid_date:dict = check_date(date)
    valid_time:dict = check_duration(time)
    valid_dist:dict = check_dist_formatting(dist)
    valid_split:dict = check_duration(split, 'Split')
    valid_sr:dict = check_sr_formatting(sr)
    valid_hr:dict = check_hr_formatting(hr)
    valid_rest:dict = check_rest_formatting(rest)
    error_messages = []
    for field in [valid_date, valid_time, valid_dist, valid_split, valid_sr, valid_hr,valid_rest]:
        if not field['success']:
            error_messages.append(field['message'])
    return error_messages 


## Change Formatting 
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
    for i in [0,1,3,4,6,7,9]:
        if zero:
            if dur2[i] != '0':
                nonz = i
                zero = False
    duration = dur2[nonz:]
    return duration 


def reformat_date(date:str)->dict: #'Apr 01 2022'
#confirms input_date formatting is (three char abrev of month)+( )+(two digit day)+( )+(four digit year value). Validity of day and year are not checked here
    if len(re.findall("^[a-zA-Z]{3}\s([0-2][0-9]|[3][0-1])\s\d\d\d\d$",date)) != 1:
        error_message = 'Date formatting error: Must use first three letters of month followed by two digit day followed by 4 diget year e.g. Jan 01 2000'
        if len(date) != 11:
            error_message = 'Date formatting error: date length incorrect'
        return {'success':False, 'message': error_message}
    mm = date[:3].capitalize()
    dd = date[4:6]
    yyyy = date[7:]
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    if not mm in months: #input does not match real month
        return {'success': False, 'message': 'Date formatting error: month wrong'}
    for i in range(12):
        if months[i] == mm:
            mm = str(i+1)
    if len(mm) == 1:
        mm = '0'+mm
    return {'success':True, 'message':yyyy+'-'+mm+'-'+dd} 


def format_time(h,m,s,t:str)->str: #hh:mm:ss.d
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


## Generate dict 
# used in add_workout_manually
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

# used in Add Workout fm Image
def generate_post_wo_dict2(int_dict:dict, user_id:str, wo_dict:dict, intvl)->dict:
    num_ints = 1
    if intvl == True:
        num_ints = len(int_dict['Date'])-1   
    s = '00:0'+int_dict['Split'][0]
    s_sec = duration_to_seconds(s)
    # populate post_dict
    wo_dict['user_id'] = int(user_id)
    wo_dict['workout_date'] = int_dict['Date'][0]
    wo_dict['time_sec']= duration_to_seconds(int_dict['Time'][0])
    wo_dict['distance']=int_dict['Distance'][0]
    wo_dict['split']=s_sec
    wo_dict['sr']=int_dict['s/m'][0]
    if int_dict['HR'][0].lower() == 'n/a':
        wo_dict['hr'] = 0
    else:
        wo_dict['hr']=int_dict['HR'][0]
    wo_dict['intervals']=num_ints
    wo_dict['comment']=int_dict['Comment'][0]
    return wo_dict 


def wo_details_df(wo_id):
    df= {'Time':[], 'Distance':[], 'Split':[], 's/m':[], 'HR':[], 'Rest':[], 'Comment':[]}
    flask_wo_details = get_wo_details(wo_id)
    wo_data = flask_wo_details['workout_summary']
    intrvl_data = flask_wo_details['intervals']
    single_td:bool = flask_wo_details['single'] 
    wo_name = find_wo_name(single_td, wo_data, intrvl_data)
    if not single_td: #interval workout
        av_rest = calc_av_rest(intrvl_data)
    else:
        av_rest = 'N/A' # single wo - no rest
    df['Time'].append(seconds_to_duration(wo_data[3])),
    df['Distance'].append(wo_data[4]),
    df['Split'].append(seconds_to_duration(wo_data[5])),
    df['s/m'].append(wo_data[6]),
    df['HR'].append(wo_data[7]),
    df['Rest'].append(av_rest),
    df['Comment'].append(wo_data[9])
    for key in ['Time','Distance','Split','s/m','HR','Rest','Comment']:
        df[key].append(" ")
    for i in range(len(intrvl_data)):
        df['Time'].append(seconds_to_duration(intrvl_data[i][2])),
        df['Distance'].append(intrvl_data[i][3]),
        df['Split'].append(seconds_to_duration(intrvl_data[i][4])),
        df['s/m'].append(intrvl_data[i][5]),
        df['HR'].append(intrvl_data[i][6]),
        df['Rest'].append((intrvl_data[i][7])),
        if df['Rest'][i] == 0:
            df['Rest'][i] = 'n/a'
        df['Comment'].append((intrvl_data[i][8]))
    date = wo_data[2] 
    return df, date, wo_name
   
## OTHER
def choose_title(radio, num_rows): #No test needed
    if radio == 'Intervals':
        head = f'## Input Interval {num_rows-1}'
    else:
        head = f'## Input Sub-Workout {num_rows-1}'
    return head  


def calc_av_rest(idata):
    sum_rest = 0
    for i in range(len(idata)):
        sum_rest += idata[i][7]
    av_rest = sum_rest/len(idata)
    return av_rest


# NOTE: even sinle time/dist wo have multiple entries (eg 2k is broken into 4x500m)
def format_and_post_intervals(wo_id, i_dict, intrvl_wo=True):
    post_intrvl_dict_template = {'workout_id':wo_id,'time_sec':None,'distance':None,'split':None,'sr':None,'hr':None,'rest':None,'comment':None, 'intrvl_wo':intrvl_wo}
    for i in range(1,len(i_dict['Date'])):
        ipost_dict = post_intrvl_dict_template
        ipost_dict['time_sec'] = duration_to_seconds(i_dict['Time'][i])
        ipost_dict['distance'] = i_dict['Distance'][i]
        ipost_dict['split'] = duration_to_seconds("00:0"+i_dict['Split'][i])
        ipost_dict['sr'] = i_dict['s/m'][i]
        if i_dict['HR'][i].lower() == 'n/a':
            ipost_dict['hr'] = 0
        else: 
            ipost_dict['hr'] = i_dict['HR'][i]
        if i_dict['Rest'][i].lower() == 'n/a':
            ipost_dict['rest'] = 0
        else: 
            ipost_dict['rest'] = i_dict['Rest'][i]
        ipost_dict['comment'] = i_dict['Comment'][i]
        post_new_interval(ipost_dict)    
    return


def find_wo_name(single:bool, wo_summary, intrvl_data):
    wo_type = 'time'
    for i in range(1,len(intrvl_data)):
        if intrvl_data[i][2] != intrvl_data[i-1][2]:
            wo_type = 'distance'
            break 
    #single time/dist
    if single: 
        if wo_type == 'time':
            name = 'Single Time: ' + str(seconds_to_duration(wo_summary[3])) #get time from wo_summary
        else:
            name = 'Single Distance: '+str(wo_summary[4])+'m' #distance from wo_summary in meters 
        return name
    # Interval time/dist
    num_ints = len(intrvl_data)
    if wo_type == 'time':
        name = 'Intervals Time: '+str(num_ints)+'x'+str(seconds_to_duration(intrvl_data[0][2]))+'/'+str(intrvl_data[0][7])+'r'
    else:
        name = 'Intervals Distance: '+str(num_ints)+'x'+str(intrvl_data[0][3])+'m'+'/'+str(intrvl_data[0][7])+'r'   
    return name

    


    