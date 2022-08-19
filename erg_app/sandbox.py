import requests
import json
from erg_app.constants import ROOT_URL

x = requests.get(ROOT_URL+'/usernames').json()
print(x)
id = requests.get(ROOT_URL+'/userid/guest').json()
print(id)

