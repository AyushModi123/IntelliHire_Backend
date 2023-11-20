from fastapi import HTTPException
from pydantic import BaseModel,  constr, ValidationError, validator, EmailStr
from typing import List, Dict, Optional


class SignupSchema(BaseModel):
    name: constr(min_length=3, max_length=50)
    email: EmailStr  
    mob_no: constr(min_length=10, max_length=13)
    password1: constr(min_length=8, strict=True)
    password2: constr()
    company_name: Optional[str]
    location: constr(min_length=1)
    role: constr(regex="^(employer|applicant)$")
    is_premium: Optional[bool]
    company_desc: Optional[str]

    @validator('password2')
    def passwords_match(cls, value, values, **kwargs):
        if 'password1' in values and value != values['password1']:
            raise HTTPException(status_code=422, detail='Passwords do not match')
        return value

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8, strict=True)

class JobFitOptionsSchema(BaseModel):    
    option: str 
    answer: bool 

class JobFitQuestionSchema(BaseModel):
    question: str
    quiz_question_options: List[JobFitOptionsSchema]
    
class JobDetailsSchema(BaseModel):
    description: constr(min_length=50)
    weights: str
    title: constr(min_length=1)
    status: constr(regex="^(active|inactive)$")
    quiz_questions: List[JobFitQuestionSchema]
    aptitude_difficulty: constr(regex="^(easy|medium|hard|mix)$")
    skill_difficulty: constr(regex="^(easy|medium|hard|mix)$")
    

    # @validator('weights')
    # def validate_my_list(cls, value):
    #     if not all((isinstance(item, float) and item<=1 and item>=0) for item in value):
    #         raise HTTPException(status_code=400, detail='All elements in the list must be floating-point')
    #     if len(value) != 7:
    #         raise HTTPException(status_code=400, detail='Weights array size should be 7')
    #     return value
    
class JobDescriptionSchema(BaseModel):
    job_title: constr(min_length=1) 
    domain: constr(min_length=1)
    tone: constr(min_length=1)

class JobFitSchema(BaseModel):
    job_description: constr(min_length=1)
    exclude_ques: Optional[List[str]]

class AnswerSubSchema(BaseModel):
    id: int 
    answer_index: int

class JobFitScoreSchema(BaseModel):
    answers: List[AnswerSubSchema]    

class AptitudeScoreSchema(BaseModel):
    answers: List[AnswerSubSchema]    

class SkillScoreSchema(BaseModel):
    answers: List[AnswerSubSchema]