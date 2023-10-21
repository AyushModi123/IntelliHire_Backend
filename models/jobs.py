from pydantic import BaseModel,  constr, ValidationError, validator
from typing import List, Dict

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