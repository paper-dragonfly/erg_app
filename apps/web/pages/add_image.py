import requests
import pandas as pd
import pdb
from constants import ROOT_URL
from dash import Dash, dcc, html, register_page, callback, Input, Output, State 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from apps.web.dash_fxs import format_and_post_intervals, format_time, duration_to_seconds, post_new_workout, check_date, check_duration, generate_post_wo_dict, format_and_post_intervals
from dash.exceptions import PreventUpdate
import cv2
import pytesseract
import datetime
import base64
import numpy as np
from matplotlib import pyplot as plt

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

file_name = 'ocr/temp/cr_erg01.jpg'
image = cv2.imread(file_name)

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
        print(ocr_dict)
    return ocr_dict

clean_ocr = basic_clean(extract_data(snip(preprocess(image))))

## TEST CONNECT

def layout(user_id=1):
    return dbc.Container([
        dcc.Store(id='user_id', data=user_id),
        dcc.Markdown('# Add Workout'),
        dcc.RadioItems(options=['Single Time/Distance','Intervals'], value='Single Time/Distance', id='radio_select'),
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-image',
                    children=html.Button('Upload Image', id="upload_image")),
                dcc.Store(id='raw_ocr', data=None),
                html.Div(id='output-upload')]),
            dbc.Col([
                dcc.Store(id='ocr_dict', data=None),
                dcc.Markdown('second col')
        ])])])

@callback(
    Output('output-upload', 'children'),
    Output('raw_ocr', 'data'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    State('upload-image', 'last_modified'))
def update_output(contents, filename, date):
    if contents is not None:
        data = contents
        children = dbc.Container([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),
            # HTML images accept base64 encoded strings in the same format
            # that is supplied by the upload
            html.Img(src=contents,id='erg_pic'),
            html.Hr(),
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])
        return children, data


## END TUTORIAL