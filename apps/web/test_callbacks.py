from conftest import app 
from dash_front import app as dash_app
import cv2
from apps.web.pages.add_image import extract_ocr, fill_form, empty_intrvl_table, stage_interval
import apps.web.dash_front as dfront
from pytest import raises
import dash_bootstrap_components as dbc
import dash_fxs as dfx
from apps.web.dash_fxs import flask_client_get as client_get, flask_client_post as client_post, reformat_date
from apps.api.logic import db_connect
import apps.web.conftest as c
import pdb
from apps.web.pages.new_user import populate_team_dropdown, display_team_input, set_user_team, submit_user
from dash.exceptions import PreventUpdate

# KEY
# 00 : Not connected to app fn
# 01 : dash_front.py
# 02 : new_user.py
# 03 : add_image.py

def test_00_populate_test_db():
    """
    NOTE: not testing a function
    Add entries to the test db to be used to test all GET functions 
    """
    try:
        conn, cur= db_connect('testing', True)
        cur.execute("INSERT INTO team(team_id,team_name) VALUES (%s,%s),(%s,%s) ON CONFLICT DO NOTHING", (1,'utah crew', 2, 'tumbleweed'))
        cur.execute("INSERT INTO users(user_id, user_name, dob, sex, team) VALUES(%s,%s,%s,%s,%s),(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", (1,'kaja','1994-12-20','Female',1,2,'moonshine','1991-01-01','Male',2))
    finally:
        cur.close()
        conn.close()

# dash_fxs functions 
def test_01_A_get_usernames(client):
    # call fx
    name_list = dfx.get_usernames(get=client_get,get_args={'client':client} )
    assert name_list == ['Kaja', 'Moonshine']


# new_user.py
def test_02_populate_team_dropdown(client):
    team_list = populate_team_dropdown('None', client_get, {'client':client})
    assert team_list == ['utah crew', 'tumbleweed', 'None', 'Other']


def test_02_display_team_input():
    assert display_team_input('Other') == {'display':'block'}
    with raises(PreventUpdate):
        display_team_input('fish')

#post
# def test_submit_user(client):
#     with raises(PreventUpdate):
#         submit_user(0,'name','dob','sex','t','p','pa')
#     output = submit_user(1,'jam','2000-01-01','Female','tumbleweed',client_post, {'client':client})
#     assert output[0] == 'User Added'
#     assert output[3] != 0
#     output2 = submit_user(1,'jam','2000-01-01','Female','tumbleweed',client_post, {'client':client})
#     assert output2[0] == 'Submit User'
#     assert output2[2] == {'display':'block'}
#     assert output2[3] == 0

## PAGE: add_image.py
# TODO: callbacks
# upload_img #skip imgs too complicated
# convert_to_cv2_compatible #skip imgs too complicated
# post_wo_to_db # skip post

# extract_ocr 
# fill_form_wo_summary
# stage_interval 

def test_03_extract_ocr():
    """
    GIVEN a cv2 compatible image
    ASSERT fn returns dict
    """
    filepath = '/Users/katcha/NiCode_Academy/ErgApp/ocr/temp/cr_erg01.jpg'
    img = cv2.imread(filepath)
    ocr_output = extract_ocr(img)
    assert type(ocr_output) == dict

ocr_result_erg01 = {'wo': ['4'], 'date': 'soy 19 2021', 'summary': ['h00.0', '1048', '1545', '21'], 'time': ['L000', '2:00.0', 'B00.0', '4.00.0'], 'dist': ['263', '263', '258', '26u'], 'split': ['1:51.5', '1:54.0', '1:56.2', '1:55.3'], 'sr': ['31', '30', '31']}

def test_03_fill_form_wo_summary():
    """
    GIVEN a raw_ocr dict
    CONFIRM error is raised if no raw_ocr
    ASSERT form is filled with summary data as expected when img initially uploaded
    CONFIRM PreventUpdate raised (form not populated with next interval) if formatting in incorrect
    GIVEN a 'submit interval' click and properly formatted form
    ASSERT form filled with next interval
    """
    raw_ocr = ocr_result_erg01
    with raises(PreventUpdate):
        fill_form(None, 0, 'f', 'r', 'd','df')
    output = fill_form(raw_ocr, 0, False, 'Single Time/Distance', None, empty_intrvl_table ) 
    assert output == (raw_ocr['date'], raw_ocr['summary'][0], raw_ocr['summary'][1], raw_ocr['summary'][2], raw_ocr['summary'][3], 'n/a', 'n/a', 4)
    with raises(PreventUpdate):
        fill_form(raw_ocr, 1, False, 'r', 'd','df')
    output = fill_form(raw_ocr, 1, True, 'r','2000-01-01',{'Time':[1]})
    assert output == ('2000-01-01', 'L000', '263', '1:51.5', '31', 'n/a', 'n/a', 4)


def test_03_reformat_date():
    """
    GIVEN a user_input date in format 'Jan 01 2000' ASSERT returns date in yyyy-mm-dd 
    GIVEN a badly formatted user_input
    ASSERT returns expected error
    """
    assert reformat_date('Jan 01 2000') == ('2000-01-01', 'success')
    assert reformat_date('pottery') == (False, 'date length incorrect')
    assert reformat_date('joy 01 2000') == (False, 'month wrong')


def test_03_stage_interval():
    """
    GIVEN 'Submit Interval' btn is clicked 
    IF formatting is correct 
    ASSERT df as expected and alert not displayed
    """
    output = stage_interval(1, 'Jan 01 2000', '4:00.0', '1048', '1:54.5', '22','n/a','n/a','4min',empty_intrvl_table, 'Title', 'single',4)
    assert output[2] == {'Date':['2000-01-01'], 'Time':['00:04:00.0'],'Distance':['1048'], 'Split': ['1:54.5'], 's/m':['22'],'HR':['n/a'],'Rest':['n/a'], 'Comment':['4min']}
    assert output[3] == None
    assert output[5] == True


        
