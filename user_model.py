from pydantic import BaseModel,  constr, ValidationError, validator
from typing import List, Dict

class UserSignup(BaseModel):
    fullname: constr(min_length=3, max_length=50)
    email: constr(min_length=3, regex=r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
    employer: constr(min_length=1, max_length=50)
    password1: constr(min_length=8, strict=True)
    password2: constr(min_length=8, strict=True)

    @validator('password2')
    def passwords_match(cls, value, values, **kwargs):
        if 'password1' in values and value != values['password1']:
            raise ValueError('Passwords do not match')
        return value


class UserLogin(BaseModel):
    email: constr(min_length=3, regex=r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
    password: constr(min_length=8, strict=True)


class JobDetails(BaseModel):
    jd: constr(min_length=10)
    weights: List[float]
    job_title: constr(min_length=2)
    status: constr(min_length=1)

    @validator('weights')
    def validate_my_list(cls, value):
        if not all((isinstance(item, float) and item<=1 and item>=0) for item in value):
            raise ValueError('All elements in the list must be floating-point')
        if len(value) != 7:
            raise ValueError('Weights array size should be 7')            
        
        return value