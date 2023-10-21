from fastapi import APIRouter
from models import UserSignup, UserLogin
from db import employer_records
from fastapi import HTTPException, Depends
import bcrypt
from auth import create_access_token
from fastapi.responses import JSONResponse, Response
router = APIRouter(tags=["Users"])

@router.post("/signup")
async def signup(user_data: UserSignup):
    data = user_data.dict()
    user = data.get("fullname")
    email = data.get("email")
    employer = data.get("employer")
    password1 = data.get("password1")
    password2 = data.get("password2")
    
    email_found = employer_records.find_one({"email": email})
    if email_found:
        raise HTTPException(status_code=400, detail="This email already exists in the database")
    else:
        hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
        user_input = {'name': user, 'employer': employer, 'email': email, 'password': hashed}
        r_id = str(employer_records.insert_one(user_input).inserted_id)
        access_token = create_access_token({"sub": email})
        return JSONResponse(content={'access_token': access_token, 'r_id': r_id}, status_code=201)

@router.post("/login")
async def login(user_data: UserLogin):
    email = user_data.email
    password = user_data.password
    
    email_found = employer_records.find_one({"email": email})
    if email_found :
        r_id = str(email_found['_id'])
        email_val = email_found['email']
        password_val = email_found['password']
        if bcrypt.checkpw(password.encode('utf-8'), password_val):
            access_token = create_access_token({"sub": email})
            return JSONResponse(content={'access_token': access_token, 'r_id': r_id}, status_code=200)    
    raise HTTPException(status_code=401, detail="Email or Password do not match.")
