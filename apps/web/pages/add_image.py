import pandas as pd
import pdb
from dash import Dash, dcc, html, register_page, callback, Input, Output, State 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from apps.web.dash_fxs import format_and_post_intervals, format_time2, generate_post_wo_dict2, post_new_workout, check_date, check_duration, format_and_post_intervals, reformat_date
from dash.exceptions import PreventUpdate
import cv2
import pytesseract
import datetime
import base64
import numpy as np
from matplotlib import pyplot as plt
import re

register_page(__name__,path_template='/upload_image/<user_id>')

## PLAN 
# upload image
# crop (skip for now)
# convert to binary/json
    # uploaded as base64 encoded str, need to convert to
    # cv2.imread - what is it reading? what format? 
# send data to img processing pipeline
# send back results dict
# populate form with data - make form editable for corrections
# submit workout


## Image OCR
def preprocess(image): #image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bw_gaussian = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,6)
    # noise removal
    image = bw_gaussian
    kernel = np.ones((2,2), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return image 

def snip(img)->dict:
    sr = img[182:400, 380:440]
    split = img[180:400, 280:385]
    dist = img[180:400, 180:280]
    time = img[180:400, 50:180]
    summary = img[135:175, 50:480]
    date = img[47:100, 10:225]
    workout = img[15:55, 10:150]
    snips = {'wo':workout, 'date':date, 'summary':summary, 'time':time, 'dist':dist, 'split':split, 'sr':sr}
    return snips

def extract_data(snips:dict)->dict:
    ocr_dict = {}
    for s in snips:
        if s in ['wo', 'date', 'summary']:
            psm = '--psm 13'
        else:
            psm ='--psm 6'
        gray = cv2.cvtColor(snips[s], cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (1,1), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        data = pytesseract.image_to_string(thresh, lang='eng', config=psm)
        ocr_dict[s] = data
    return ocr_dict

def basic_clean(ocr_dict:dict):
    for key in ocr_dict:
        ocr_dict[key] = ocr_dict[key].strip('\n\'"~|°`‘-!“ [()><')
        ocr_dict[key]=ocr_dict[key].replace("\n", ' ')
        ocr_dict[key]=ocr_dict[key].replace(",", '.')
        s2 = ""
        for i in range(len(ocr_dict[key])):
            if not ocr_dict[key][i] in ['\\','|','-', '“']:
                s2 += ocr_dict[key][i]
        ocr_dict[key] = s2
        if not key == 'date':
            ocr_dict[key]=ocr_dict[key].replace("A", '4') 
        if key != 'date':
            ocr_dict[key] = ocr_dict[key].split()         
    return ocr_dict

#put ocr extraction into one func
def clean_ocr(image):
    return basic_clean(extract_data(snip(preprocess(image))))


### Empty forms 
empty_single_table = {'Date':[],'Time':[],'Distance':[],'Split':[],'s/m':[],'HR':[],'Comment':[]}
empty_post_wo_dict = {'user_id':None, 'workout_date':None,'time_sec':None,'distance':None,'split':None,'sr':None,'hr':None,'intervals':1, 'comment':None}
empty_intrvl_table = {'Date':[],'Time':[],'Distance':[],'Split':[],'s/m':[],'HR':[],'Rest':[],'Comment':[]}
empty_post_intrvl_dict = {'workout_id':None,'time_sec':None,'distance':None,'split':None,'sr':None,'hr':None,'rest':None,'comment':None}


def layout(user_id=1):
    return dbc.Container([
        dcc.Store(id='user_id', data=user_id),
        dcc.Markdown('# Add Workout'),
        dcc.RadioItems(options=['Single Time/Distance','Intervals'], value='Single Time/Distance', id='radio_select'),
        dbc.Row([
        # Upload + Display image
            dbc.Col([
                dcc.Upload(
                    id='upload-image',
                    children=html.Button('Upload Image', id="upload_image")),
                dcc.Store(id='base64_img', data=None),
                dcc.Store(id='np_array_img', data=None),
                dcc.Store(id='raw_ocr', data=None),
                html.Div(id='output-upload')]),
        # data form feilds
            dbc.Col([
                dcc.Store(id='ocr_dict', data=None),
                dcc.Markdown('## Workout Summery', id='h2_input_form'),
                dbc.Row([
                    dbc.Col(dbc.Label('Date',html_for='ui_date2'), width=2),
                    dbc.Col(dcc.Input(placeholder='Jan 01 2000',id="ui_date2", size='20' ), width=4)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Time',html_for='ui_time2'), width=2),
                    dbc.Col(dcc.Input(placeholder='hh:mm:ss.t', id='ui_time2', size='15', maxLength=12), width=4)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Distance',html_for='ui_dist2'), width=2),
                    dbc.Col(dcc.Input(placeholder='meters',id="ui_dist2", size='10'), width=4)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Split',html_for='ui_split2'), width=2),
                    dbc.Col(dcc.Input(placeholder='m:ss.d',id="ui_split2", size='10'), width=4)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Stroke Rate',html_for='ui_sr2'), width=2),
                    dbc.Col(dcc.Input(placeholder='s/m',id="ui_sr2", size='10'), width=4)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Heart Rate',html_for='ui_hr2'), width=2),
                    dbc.Col(dcc.Input(placeholder='BPM',id="ui_hr2", size='10'), width=4)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Comment',html_for='ui_com2'), width=2),
                    dbc.Col(dcc.Input('',id="ui_com2", size='20'), width=8)
                    ]),
                dbc.Row([
                    dbc.Col(dbc.Label('Rest',html_for='ui_rest2'), width=2),
                    dbc.Col(dcc.Input(placeholder='seconds',id="ui_rest2", size='10'), width=4)
                    ]),
                # End of form
                dbc.Button('Submit Interval', id='interval_submit2', n_clicks=0, color='primary'),
                dbc.Alert(id='intrvl_alert2', style={'display':'none'},color='warning'),
                dbc.Alert(id='all_added_alert', children='Full Workout Staged', color='info', style={'display':'none'}),
                dcc.Store(id='intrvl_count', data=None),
                dcc.Store(id='int_dict2', data=empty_intrvl_table),
                dcc.Store(id='intrvl_formatting_approved2', data=False),
                dbc.Row(
                    [dbc.Table.from_dataframe(pd.DataFrame(empty_intrvl_table),striped=True,bordered=True)], 
                    id='interval_table2'),
                dbc.Button('Submit workout', id='btn_submit_workout2', n_clicks=0, color='primary')
                ], id='form_col')
        ])])

#upload pic
@callback(
    Output('output-upload', 'children'),
    Output('base64_img', 'data'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    State('upload-image', 'last_modified'))
def upload_img(contents, filename, date):
    if contents is not None:
        base64_img = contents[23:]
        print('b64: ', type(base64_img))
        children = dbc.Container([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            # HTML images accept base64 encoded strings in the same format
            # that is supplied by the upload
            html.Img(src=contents,id='erg_pic'),
            html.Hr()
            ])
        return children, base64_img


@callback(
    Output('np_array_img', 'data'),
    Input('base64_img', 'data')
)
def convert_to_cv2_compatible(b64):
    if b64 is not None:
        print('run convert to cv2 compatible')
        b64_bytes = b64.encode('ascii')
        im_bytes = base64.b64decode(b64_bytes)
        im_arr = np.frombuffer(im_bytes, dtype=np.uint8) # im_arr is one-dim np array
        img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
        return img


@callback(
    Output('raw_ocr', 'data'),
    Input('np_array_img', 'data')
)
def extract_ocr(image):
    if image is not None: 
        image = np.array(image, dtype='uint8')
        # image = np.uint8(image) WHAT IS A DICT?
        img = preprocess(image)
        snips:dict = snip(img)
        ocr_dict:dict = extract_data(snips)
        clean_ocr:dict = basic_clean(ocr_dict)
        # clean_ocr = basic_clean(extract_data(snip(preprocess(image))))
        print(clean_ocr)
        return clean_ocr 


@callback(
    Output('ui_date2', 'value'),
    Output('ui_time2', 'value'),
    Output('ui_dist2', 'value'),
    Output('ui_split2', 'value'),
    Output('ui_sr2', 'value'),
    Output('ui_hr2', 'value'),
    Output('ui_rest2','value'),
    Output('intrvl_count', 'data'),
    Input('raw_ocr', 'data'),
    Input('interval_submit2', 'n_clicks'),
    Input('intrvl_formatting_approved2','data'),
    State('radio_select','value'),
    State('ui_date2', 'value'),
    State('int_dict2', 'data')
)
def fill_form(raw_ocr, n_clicks, formatted, radio, date, df):
    if not raw_ocr:
        raise PreventUpdate 
    num_ints = len(raw_ocr['time'])
    hr = 'n/a'
    rest = 'n/a'
    if radio == 'Intervals':
        rest = None  
    if n_clicks == 0: 
        if len(raw_ocr['summary']) == 5:
            hr = raw_ocr['summary'][4] 
        return raw_ocr['date'], raw_ocr['summary'][0], raw_ocr['summary'][1], raw_ocr['summary'][2], raw_ocr['summary'][3], hr, rest, num_ints
    # if len(df['Time']) == 0:
    #     print('blocked by df len')
    #     raise PreventUpdate
    if not formatted:
        print('blocked formatted  == False')
        raise PreventUpdate 
    else:
        i = len(df['Time'])-1
        if i < num_ints: 
            return date, raw_ocr['time'][i], raw_ocr['dist'][i], raw_ocr['split'][i], raw_ocr['sr'][i], hr, rest, num_ints
        else: 
            return date, None, None, None, None, None, None, num_ints 
    


# Add intervals to inverval table
@callback(
    Output('h2_input_form', 'children'), #form title
    Output('interval_table2','children'), #table
    Output('int_dict2','data'), #table contents
    Output('intrvl_alert2','children'), #alert message
    Output('intrvl_alert2', 'style'), #alert visibility
    Output('intrvl_formatting_approved2','data'), #formatting approval
    Output('all_added_alert', 'style'), 
    Input('interval_submit2', 'n_clicks'),
    State('ui_date2','value'),
    State('ui_time2', 'value'),
    State('ui_dist2', 'value'),
    State('ui_split2', 'value'),
    State('ui_sr2', 'value'),
    State('ui_hr2', 'value'),
    State('ui_rest2', 'value'),
    State('ui_com2', 'value'),
    State('int_dict2', 'data'),
    State('h2_input_form', 'children'),
    State('radio_select', 'value'),
    State('intrvl_count', 'data')
)
def stage_interval(n_clicks, date, time, dist, split, sr, hr, rest, com, df,head, radio, num_intrvls):
    if n_clicks == 0:
        raise PreventUpdate
    complete_alert = {'display':'none'}
    blank_table=dbc.Table.from_dataframe(pd.DataFrame(df), striped=True, bordered=True)
    # check format of inputs
    date, message = reformat_date(date) #yyyy-mm-dd
    if not date:
        alert_message = f'Date formatting wrong: {message}'
        return head, blank_table, df, alert_message, {'display':'block'}, False, complete_alert
    valid_date:dict = check_date(date)
    if not valid_date['accept']:
        alert_message = 'Date formatting wrong: '+valid_date['message']
        return head, blank_table, df, alert_message, {'display':'block'}, False,complete_alert
    time:str = format_time2(time) #hh:mm:ss.d
    valid_time = check_duration(time)
    if not valid_time['accept']:
        alert_message = 'Time formatting wrong: '+valid_time['message']
        return head, blank_table, df, alert_message, {'display':'block'}, False,complete_alert
    wsplit = '00:0'+split 
    valid_split = check_duration(wsplit)
    if not valid_split['accept']:
        alert_message = 'Split formatting wrong: '+valid_split['message']
        return head, blank_table, df, alert_message, {'display':'block'}, False,complete_alert
    if len(re.findall('\A\d\d\Z', sr)) != 1:
        alert_message = 'Stroke Rate formatting wrong: must be integer'
        return head, blank_table, df, alert_message, {'display':'block'}, False, complete_alert
    df['Date'].append(date)
    df['Time'].append(time)
    df['Distance'].append(dist)
    df['Split'].append(split)
    df['s/m'].append(sr)
    df['HR'].append(hr)
    df['Rest'].append(rest)
    df['Comment'].append(com)
    if radio == 'Intervals':
        head = '## Input Interval'
    else:
        head = '## Input Sub-Workout'
    if len(df['Time']) == num_intrvls+1:
        complete_alert = {'display': 'block'} 
    return head, dbc.Table.from_dataframe(pd.DataFrame(df), striped=True, bordered=True), df, None, {'display':'none'}, True,complete_alert


#Post wo to db 
@callback(
    Output('btn_submit_workout2', 'children'),
    Output('btn_submit_workout2', 'color'),
    Input('btn_submit_workout2', 'n_clicks'),
    State('intrvl_formatting_approved2', 'data'),
    State('int_dict2', 'data'),
    State('user_id', 'data'),
    State('radio_select', 'value')
)
def post_wo_to_db(n_clicks, formatting_approved, int_dict, user_id, radio):
    if n_clicks==0 or not formatting_approved:
        raise PreventUpdate
    intrvl = False
    if radio == 'Intervals':
        intrvl = True
    wo_dict = generate_post_wo_dict2(int_dict, user_id, empty_post_wo_dict, intrvl)
    print(wo_dict)
    wo_id = post_new_workout(wo_dict)['workout_id']
    format_and_post_intervals(wo_id, int_dict, intrvl)
    return 'Interval Workout Submitted!', 'success'