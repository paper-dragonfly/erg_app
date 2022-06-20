from erg_app import erg_front as front
from erg_app.logic import db_connect
import erg_app.conftest as c 
import pdb

def test_duration_to_seconds():
    secs = front.duration_to_seconds('00:01:40.00')
    assert secs == 100

def mock(input_values:list, func, **kwargs):
    pdb.set_trace()
    output = []
    printed = []
    front.input = lambda s : input_values.pop(0)
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
    # populate db with user 
    try: 
        #populate db with user 
        conn, cur = db_connect('testing', True)
        cur.execute("INSERT INTO users(user_id, user_name) VALUES(%s, %s) ON CONFLICT DO NOTHING",(1,'kaja'))
        # call login()
        output, printed = mock(['2','kaja'], front.login)
        assert output == [1, 'kaja']
        assert printed == ['\nLOGIN', '1. List Users \n2. Search by User Name', "kaja logged in" ]  
    finally: 
        cur.close()
        conn.close()
        c.clear_test_db()

        # TODO need to add command line argument parsing (argparse) 
    
# def test_create_new_user(client):
#     input_values = []


# def create_new_user()->tuple:
#     print('\nCreate New User')
#     user_name = input('User Name: ')
#     age = input_int('Age: ')
#     sex = input_sex('Sex (</F): ') 
#     team = input("Team: " )
#     newuser_dict = {'user_name': user_name, "age": age, 'sex':sex, 'team': team}
#     #POST newuser_dict to /newuser
#     url = ROOT_URL+'/newuser'
#     flask_resp = requests.post(url, json=newuser_dict).json()
#     user_id:int = flask_resp['user_id'] 
#     print(f'\nNew user created. Welcome {user_name}')
#     return user_id, user_name





 