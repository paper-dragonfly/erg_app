import requests
import json
from erg_app.constants import ROOT_URL
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

    