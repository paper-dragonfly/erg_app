from erg_app import erg_front as front
from erg_app.constants import ROOT_URL
from erg_app.logic import db_connect
import erg_app.conftest as c 
import pdb

def test_duration_to_seconds():
    secs = front.duration_to_seconds('00:01:40.00')
    assert secs == 100

def mock(input_values:list, func, **kwargs):
    output = []
    printed = []
    # patch input() so that when called next value in output:lst is submitted 
    pdb.set_trace()
    front.input = lambda s : input_values.pop(0)
    # patch print() so when called str is appended to printed:lst
    front.print = lambda s : printed.append(s)
    while input_values:
        out = func(**kwargs) 
        output.append(out)
    return output, printed  

def test_input_sex():
    output, printed = mock(["M",'f','house',""], front.input_sex, prompt_str="")
    assert output == ['M','F',""]
    assert printed == ['Must select M or F']

def test_input_int():
    output, printed= mock(['2',"",'five','1'], front.input_int, prompt_str="")
    assert output == [2,"",1]
    assert printed == ['Input must be integer']

def test_input_duration():
    output, printed = mock(['01:00:20.55','00:15:00', 'fish', '25:00:00.00','00:01:002', '00:02:23.aa', '01:01:01.01'], front.input_duration, prompt_str="")
    assert output == ['01:00:20.55','00:15:00.00', '01:01:01.01'] 
    assert printed == ['Must use hh:mm:ss.dd formatting','hours out of range', 'Input length incorrect', 'ms formatting incorrect']

def test_input_date():
    output, printed = mock(['2000-02-30','2000-01-32','2000-15-01','2000/01/01','2000-01-01'], front.input_date, prompt_str="")
    assert output == ['2000-01-01']
    assert printed == ['day out of range','day out of range','month out of range','Must use yyyy-mm-dd formatting']

def test_input_interval_type():
    output, printed = mock(['fish','DARK', 'distance'], front.input_interval_type, prompt_str="")
    assert output == ['distance', 'distance']
    assert printed == ['Invalid entry, try agian']
    # anything starting with d or t will be converted to a valid entry. I'm ok with this. 

def test_create_new_workout_dict():
    output, printed = mock(['2000-01-01','2000','00:08:00.00','00:02:00.00','3','2k'],front.create_new_workout_dict,workout_type=3,user_id=1)
    assert output == [{'user_id':1,'date':'2000-01-01','distance':2000,'time_sec':480, 'split':120, 'intervals':3,'comment':'2k' }]
    assert printed == [] 

    output, printed = mock(['2000-01-01','2000','00:08:00.00','00:02:00.00','2k'],front.create_new_workout_dict,workout_type=1,user_id=1)
    assert output == [{'user_id':1,'date':'2000-01-01','distance':2000,'time_sec':480, 'split':120, 'intervals':1,'comment':'2k' }]
    assert printed == [] 

def test_create_intervals_dict():
    mock_inputs = [12000,'01:30:00.00','00:02:10.00', '00:01:00']
    output, printed = mock(mock_inputs, front.create_intervals_dict,workout_id=1,interval=2, interval_type='distance')
    assert output == [{'workout_id':1,'interval_type':'distance','distance':12000,'time_sec':5400,'split':130,'rest':60}]
    assert printed == ['Interval 2'] 

def test_create_logsearch_dict():
    mock_inputs = ['2000-01-01',24000,"",""]
    output, printed = mock(mock_inputs, front.create_logsearch_dict)
    assert output == [{'date':'2000-01-01','distance':24000}]
    assert printed == ['Search by different parameters, press enter to skip a param'] 

    mock_inputs = ["","","",""]
    output, printed = mock(mock_inputs, front.create_logsearch_dict)
    assert output == [{}]
    assert printed == ['Search by different parameters, press enter to skip a param'] 

    mock_inputs = ["2000-17-01",'2000-01-01',"","",""]
    output, printed = mock(mock_inputs, front.create_logsearch_dict)
    assert output == [{'date':'2000-01-01'}]
    assert printed == ['Search by different parameters, press enter to skip a param','month out of range'] 

def test_login(client):
    try: 
        #populate db with user 
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(5,'sasha'))
        # call login()
        output, printed = mock(
            ['2','sasha'], 
            front.login,
            get=front.flask_client_get,
            get_args={'client':client},
            post=front.flask_client_post,
            post_args={'client':client})
        assert output == [(5, 'sasha')]
        assert printed == ['\nLOGIN', '1. List Users \n2. Search by User Name', "sasha logged in" ]  
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()

    
def test_create_new_user(client):
    try:
        conn, cur = db_connect('testing', True)
        output, printed = mock(
            ['brook',14,'F','UtahCrew'],
            front.create_new_user,
            post=front.flask_client_post,
            post_args={'client': client})
        cur.execute("SELECT user_id FROM users WHERE user_name = 'brook'")
        brook_id = cur.fetchone()[0]
        assert output == [(brook_id, 'brook')]
        assert printed == ['\nCreate New User','\nNew user created. Welcome brook']
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()


def test_authenticate(client): # don't think I can do this because can't pass input_values into the sub-functions of login and creae_new_user so getting 'can't pop from empty list error'
    # TODO check with NICO if there's a fix, if not remove excess args from authenticate
    try:
        #populate db with user 
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(6,'bruno'))
        conn,cur = db_connect('testing',True)
        output, printed = mock(
            #[incorrect input, select to login, select to list users,user_name]
            ['1','1','bruno'],
            front.authenticate,
            login_get=front.flask_client_get,
            login_get_args={'client':client},
            new_user_post= front.flask_client_post,
            new_user_post_args={'client':client})
        assert output == [(6,'bruno')]
        assert printed ==["\nWelcome to ErgTracker \n1.Login\n2.Create new account",'pick an option using the coresponding bullet number','\nLOGIN', '1. List Users \n2. Search by User Name', "bruno logged in"]
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()


# TODO: NOT COMPLETE - need to figure out
def test_view_workout_log(client):
    # populate db with user and workouts
    try:
        conn, cur = db_connect('testing',True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s,%s)",(7,'emma'))
        cur.execute("INSERT INTO workout_log(workout_id, user_id, date, distance, time_sec,split,intervals,comment) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(1,1,'2022-01-01', 2000,480,120,1,'PR'))
        # call mock
        output, printed = mock(
            []
        )

    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()

### for ref
def view_workout_log(user_id, user_name,post=flask_requests_post,post_args={}):
    print('\n')
    url = ROOT_URL+'/log'
    workout_log:list = post(url, {'user_id':user_id}, **post_args)['message'] #[[...],[...]]
    # if no workouts
    if len(workout_log) == 0:
        print('No workouts for this user')
    else: 
        #display as table
        workout_log.insert(0,["workout_id","user_id","date","distance","time_sec","split","intervals","comment"])
        print(f'Workout Log for {user_name}')
        print(tabulate(workout_log, headers='firstrow'))





