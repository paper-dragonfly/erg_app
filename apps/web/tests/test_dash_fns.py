from apps.web.dash_fns import calc_av_rest, check_hr_formatting, check_rest_formatting, check_sr_formatting, find_wo_name, generate_post_wo_dict2, get_name, get_wo_details, post_newuser, check_date, check_duration, reformat_date, seconds_to_duration, validate_form_inputs, duration_to_seconds, wo_details_df
import pdb
from apps.web.dash_fns import get_usernames, flask_client_get as client_get, flask_client_post as client_post, get_id
from apps.api.logic import db_connect
from apps.web.tests.conftest import clear_test_db


def test_00_populate_test_db():
    """
    NOTE: not testing a function
    Add entries to the test db to be used to test all GET functions 
    teams x2, users x2, summ_wo x2, 
    """
    try:
        conn, cur= db_connect('testing', True)
        # populate team
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        # populate users
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
        # populate workout_log
        cur.execute("INSERT INTO workout_log(workout_id, user_id, workout_date, time_sec, distance, split, sr, hr, intervals, comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,1,'2000-01-01',120,500,120,26,155,1,'500mx1', 2,1,'2020-02-02',600,2200,122,22,160,2,'5minx2'))
        # populate interval_log
        cur.execute("INSERT INTO interval_log(interval_id, workout_id, time_sec, distance, split, sr, hr, rest, comment, interval_wo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",(1,1,120,500,120,26,155,0,'500mx1',False, 2,2,300,2200,122,22,160,60,'5minx2 i1',True,3,2,300,2200,122,22,160,60,'5minx2 i2',True))
    finally:
        cur.close()
        conn.close()

# GET 
def test_01_get_usernames(client):
    """
    When fn is called 
    Then assert returns capitalized user_names 
    """
    name_list = get_usernames(get=client_get,get_args={'client':client} )
    assert name_list == ['Kaja', 'Moonshine']


def test_02_get_id(client):
    assert get_id('kaja',client_get,{'client':client}) == 1


def test_03_get_name(client):
    assert get_name(1,client_get,{'client':client}) == 'kaja'


def test_04_get_wo_details(client): ##come back
    flask_resp_details = get_wo_details(1,client_get,{'client':client})
    assert flask_resp_details['status_code'] == 200 
    assert flask_resp_details['single'] == True 
    assert len(flask_resp_details['workout_summary']) == 10
    

def test_05_post_newuser(client):
    newuser_post_dict = {'user_name':'fox', 'dob':'2000-01-01', 'sex':'Male', 'team':'utah crew'}
    flask_resp = post_newuser(newuser_post_dict,client_post,{'client':client})
    assert flask_resp['status_code'] == 200 
    assert type(flask_resp['body']) == int


def test_06_check_date():
    assert check_date('Jan 01 2000') == {'success':True, 'message':'2000-01-01'}
    assert check_date('Jan 55 2000')['success'] ==False 
    assert check_date('Feb 31 2000')['success'] == False 
    assert check_date('Apr 31 2000')['success']==False 
    assert check_date('')['success']==True


def test_07_check_duration():
    assert check_duration('00:45:00.0')['success']==True 
    assert check_duration('1:50.2','Split')['success'] == True
    assert check_duration('fire')['success']==False 
    assert check_duration('00:99:88.8')['success']== False 


def test_08_check_sr_formatting():
    assert check_sr_formatting('22')['success']==True
    assert check_sr_formatting('100')['success']==True
    assert check_sr_formatting('ss')['success']==False
    assert check_sr_formatting("")['success'] == True 


def test_09_check_hr_formatting():
    assert check_hr_formatting('155')['success']==True
    assert check_hr_formatting('')['success']==True
    assert check_hr_formatting('n/a')['success']==True
    assert check_hr_formatting('1a')['success']==False 
    assert check_hr_formatting('155 ')['success']==False 


def test_10_rest_formatting():
    assert check_rest_formatting('60')['success']==True
    assert check_rest_formatting('60 ')['success']==False 
    assert check_rest_formatting('min')['success']==False
    assert check_rest_formatting('')['success']==True
 


def test_11_validate_form_inputs():
    assert validate_form_inputs('Jan 01 2000','8:00.0','2000','2:00.0',"33",'','n/a') == []
    assert validate_form_inputs('Jan 01 2000','8:00.0','2000','2:00.0',"33",'badhr','badrest') == ['Heart rate formatting error', 'Rest formatting error']


def test_12_duration_to_seconds():
    assert duration_to_seconds('00:01:40.0') == 100
    assert duration_to_seconds('') == 0


def test_13_seconds_to_duration():
    assert seconds_to_duration(100) == '1:40.0'
    assert seconds_to_duration(0) == '0' 
    assert seconds_to_duration(3643.2) == '1:00:43.1'


def test_14_reformat_date():
    assert reformat_date('Jan 01 2000')['message'] == '2000-01-01' 
    assert reformat_date('fire')['success'] == False 
    assert reformat_date('Jan 01 2000 ')['success'] == False 
    assert reformat_date('Her 01 2000')['success'] == False


def test_format_time():
    pass # only used in manual entry which is depricated


def test_generate_post_wo_dict():
    pass # skip - for manual entry which is depricated


def test_15_generate_post_wo_dict2():
    int_dict = {'Date':['2000-01-01','2000-01-01','2000-01-01'],'Time':['00:08:00.0','00:05:00.0','00:03:00.0'],'Distance':['2000','1000','1000'],'Split':['2:00.0','2:30.0','1:30.0'],'s/m':['22','20','24'],'HR':['155','155','155'],'Rest':['60','60','60'],'Comment':["2x1k","",""]}
    user_id = '1'
    wo_dict = {'user_id':None, 'workout_date':None,'time_sec':None,'distance':None,'split':None,'sr':None,'hr':None,'intervals':1, 'comment':None}
    interval = True 
    assert generate_post_wo_dict2(int_dict, user_id, wo_dict, interval)== {'user_id':1, 'workout_date':'2000-01-01','time_sec':480.0,'distance':'2000','split':120.0,'sr':'22','hr':'155','intervals':2, 'comment':"2x1k"}
    

def test_16_format_and_post_intervals():
    pass 


def test_17_wo_details_df(mocker):
    """
    WHEN fn is passed a wo_id
    THEN assert returns df with summary and interval data for wo AND date And wo_name"""
    # mock internal fns
    workout_summary= [(1,1,'2000-01-01',480.0,2000,120.0,22,155,2,"2x1k"),]

    intervals = [(1,1,499,1000,150,20,155,60,"slow",True),(2,1,360,1000,90,24,155,60,'fast',True)]
    # {'interval_id':[1,2],'workout_id':[1,1], 'time_sec':[400,360],'distance':[1000,1000],'split':[150,90],'sr':[20,24],'hr':[155,155],'rest':[60,60],'comment':["slow","fast"], 'interval_wo': [True, True]}

    flask_wo_details = {'status_code':200, 'single': False, 'intervals':intervals, 'workout_summary':workout_summary}
    mocker.patch('apps.web.dash_fns.get_wo_details', return_value=flask_wo_details)

    assert wo_details_df('1')[1] == '2000-01-01'
    assert wo_details_df('1')[2] =='Intervals Distance: 2x1000m/60r'
    # assert wo_details_df('1')[0] == {'Time':['8:00.0',""], 'Distance':[], 'Split':[], 's/m':[], 'HR':[], 'Rest':[], 'Comment':[]}



def test_choose_title():
    pass # Simple - no test needed


def test_18_calc_av_rest():
    intervals = [(1,1,499,1000,150,20,155,60,"slow",True),(2,1,360,1000,90,24,155,60,'fast',True)]
    assert calc_av_rest(intervals)==60


def test_19_find_wo_name():
    workout_summary= [(1,1,'2000-01-01',480.0,2000,120.0,22,155,2,"2x1k")]
    idata = [(1,1,499,1000,150,20,155,60,"slow",True),(2,1,360,1000,90,24,155,60,'fast',True)]
    single = False 
    assert find_wo_name(single,workout_summary,idata) == 'Intervals Distance: 2x1000m/60r'


def test_clear_testdb():
    clear_test_db()
    

    