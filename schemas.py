from fastapi import HTTPException
from pydantic import BaseModel,  constr, ValidationError, validator, EmailStr
from typing import List, Dict, Optional


class SignupSchema(BaseModel):
    name: constr(min_length=3, max_length=50)
    email: EmailStr  
    mob_no: constr(min_length=10, max_length=13)
    password1: constr(min_length=8, strict=True)
    password2: constr(min_length=8, strict=True)
    company_name: Optional[str]
    role: constr(regex="^(employer|applicant)$")

    @validator('password2')
    def passwords_match(cls, value, values, **kwargs):
        if 'password1' in values and value != values['password1']:
            raise HTTPException(status_code=400, detail='Passwords do not match')
        return value

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8, strict=True)

class JobDetailsSchema(BaseModel):
    description: constr(min_length=10)
    weights: List[float]
    title: constr(min_length=2)
    status: constr(regex="^(active|inactive)$")

    @validator('weights')
    def validate_my_list(cls, value):
        if not all((isinstance(item, float) and item<=1 and item>=0) for item in value):
            raise HTTPException(status_code=400, detail='All elements in the list must be floating-point')
        if len(value) != 7:
            raise HTTPException(status_code=400, detail='Weights array size should be 7')
        return value