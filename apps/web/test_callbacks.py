from dash_front import choose_page 
from pages.new_user import populate_team_dropdown
import dash_bootstrap_components as dbc

def test_choose_page():
    output = choose_page('Guest')
    assert output == [dbc.DropdownMenuItem('Home', href=f'/'),
        dbc.DropdownMenuItem('Workout Log', href=f'/log_table/1'),
        dbc.DropdownMenuItem('Add Workout', href=f'/upload_image/1'),
        dbc.DropdownMenuItem('Add Workout Manual', href=f'/addworkout/1'),
        dbc.DropdownMenuItem('Add New User', href='/newuser')]

#new_user
def test_populate_team_dropdown(): 
    output = 