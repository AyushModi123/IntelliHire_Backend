from fastapi import APIRouter
from schemas import ApplicantSignupSchema, EmployerSignupSchema, UserLoginSchema
from db import db
from fastapi import HTTPException, Depends
import bcrypt
from models.users import UsersModel, ApplicantsModel, EmployersModel
from auth import create_access_token
from fastapi.responses import JSONResponse, Response
from typing import Union
router = APIRouter(tags=["Users"])

@router.post("/signup")
async def signup(user_data:  Union[ApplicantSignupSchema, EmployerSignupSchema]):
    data = user_data.dict()
    role = data.get("role")
    email = data.get("email")    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user:
        raise HTTPException(status_code=400, detail="This email already exists in the database")
    else:
        if role == "employer":
            password = data.get("password1")            
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())            
            user_model = UsersModel(
                name=data.get("name"),
                email=email,
                mob_no=data.get("mob_no"),                               
                password=hashed_pass,
                role=role
            )
            db.add(user_model)
            employer_model= EmployersModel(
                company_name=data.get("company_name"), 
                user_id=user_model.id
            )
            db.add(employer_model)
            db.commit()             
        elif role == "applicant":
            password = data.get("password1")            
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())            
            user_model = UsersModel(
                name=data.get("name"),
                email=email,
                mob_no=data.get("mob_no"),                               
                password=hashed_pass,
                role=role
            )
            db.add(user_model)
            applicant_model = ApplicantsModel(
                user_id=user_model.id,
                job_id=data.get("job_id"),
            )
            db.add(applicant_model)
            db.commit()                         
        access_token = create_access_token({"sub": email})
        return JSONResponse(content={'access_token': access_token, 'role': role}, status_code=201)

@router.post("/login")
async def login(user_data: UserLoginSchema):
    email = user_data.email
    password = user_data.password    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user:        
        email_val = user.email
        password_val = user.password
        role = user.role        
        if bcrypt.checkpw(password.encode('utf-8'), password_val.encode('utf-8')):
            access_token = create_access_token({"sub": email_val})
            return JSONResponse(content={'access_token': access_token, 'role': role}, status_code=200)    
    raise HTTPException(status_code=401, detail="Email or Password do not match.")
