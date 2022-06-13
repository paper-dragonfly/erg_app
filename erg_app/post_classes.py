from datetime import datetime
from pydantic import BaseModel

# QUESTION: why are the variables class vars not instance cars for pydantic? 
class NewUser(BaseModel):
    user_name:str
    pw:str='password'
    sex:str='F'
    age:int=0
    team:str='private'
    weight:int=0

class IntervalWorkout(BaseModel):
    user_id:str = 'guest'
    distance:int = 0
    time:int = 0
    duration:str = '00:00:00'
    rest:int = 0
    intervals:int = 1
    date = '2000-01-01'
    userid:int = 0


