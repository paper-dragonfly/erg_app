from datetime import datetime
from pydantic import BaseModel

# QUESTION: why are the variables class vars not instance vars for pydantic? 
class NewUser(BaseModel):
    user_name:str
    dob:str
    sex:str='Female'
    team:str='private'

class IntervalWorkout(BaseModel):
    user_id:str = 'guest'
    distance:int = 0
    time:int = 0
    rest:int = 0
    intervals:int = 1
    date = '2000-01-01'
    userid:int = 0

class NewWorkout(BaseModel):
    user_id:int
    workout_date:str = '2000-01-01'
    time_sec:int = 0
    distance:int = 0
    split:int = 0
    sr:int = 0
    hr:int = 0
    intervals:int = 1
    comment:str = ""

class NewInterval(BaseModel):
    workout_id:int 
    time_sec:int
    distance:int 
    split:int=0
    sr:int=0
    hr:int=0
    rest:int=0
    comment:str=""
    interval_wo:bool


