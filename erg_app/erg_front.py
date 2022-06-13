from importlib.resources import contents
import requests
from typing import Dict, List, Tuple, Union
import pdb

CONTENTS = """
    1. View workout log
    2. Add workout
    3. Search by workout
    """

ROOT_URL = "http://localhost:500"

def login():
    print("Welcome to ErgTracker \n1.Login\n2.Create new account")
    resp = 0
    while resp != 1 and resp != 2:
        resp= input('pick an option using the coresponding bullet number: ')
    if resp == 1:
        user_name = input('User Name: ')
        #add pw later
        # TODO: change this, can't query db from front end 
        user_id = "SELECT user_id FROM users WHERE user_name = %s",(user_name,)
    elif resp == 2:
        user_name = input('User Name: ')
        age = int(input("Age: "))
        sex = input('Sex: ')
        team = input("Team: " )
        newuser_dict = {'user_name': user_name, "age": age, 'sex':sex, 'team': team} 
        # post newuser_dict to "/newuser"
        







def run():
    user_id = login()
    

    print("LOGIN")

    print(input("username: "))
    print(CONTENTS)
    page = input('Choose a page using its corresponding number: ')
    if page == 1:
        pass
    elif page == 2:
        pass
    elif page == 3:
        pass
    else:
        print('not valid entry')