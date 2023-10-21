import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, Response
from user_model import UserLogin, UserSignup, JobDetails
from user_schema import user_insert_serializer
from pymongo import MongoClient
import bcrypt
from bson import ObjectId
from dotenv import load_dotenv
import os
import uvicorn
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

MONGODB_URL = os.getenv('MONGODB_URL')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def MongoDB():
    client = MongoClient(MONGODB_URL)
    db_records = client.get_database('records')
    employer_records = db_records.employer
    applicant_records = db_records.applicant
    jd_records = db_records.jd
    result_records = db_records.result
    return employer_records, applicant_records, jd_records, result_records

employer_records, applicant_records, jd_records, result_records = MongoDB()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return email


@app.post("/signup")
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
        user_input = user_insert_serializer(user=user, employer=employer, email=email, hashed_password=hashed)
        r_id = str(employer_records.insert_one(user_input).inserted_id)
        access_token = create_access_token({"sub": email})
        return JSONResponse(content={'access_token': access_token, 'r_id': r_id}, status_code=201)

@app.post("/login")
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
            return JSONResponse(content={'access_token': access_token, 'r_id': r_id}, status_code=201)    
    raise HTTPException(status_code=401, detail="Email or Password do not match.")

@app.post('/dashboard/{r_id}')
async def post_job(r_id: str, job_data: JobDetails, current_user: str = Depends(get_current_user)):
    try:
        rec_details = employer_records.find_one({"_id": ObjectId(r_id)})			
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid Recruiter id")    
    if rec_details:
        if current_user != rec_details["email"]:
            raise HTTPException(status_code=403, detail="You do not have permission to access this route")
        data = job_data.dict()
        j_id = str(jd_records.insert_one({**data, "r_id": r_id}).inserted_id)		
        return JSONResponse(content={'j_id':j_id}, status_code=201)		
    else:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    
@app.get('/dashboard/{r_id}')
async def get_jobs(r_id: str, current_user: str = Depends(get_current_user)):
    try:
        rec_details = employer_records.find_one({"_id": ObjectId(r_id)})			
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid Recruiter id")    
    if rec_details:
        if current_user != rec_details["email"]:
            raise HTTPException(status_code=403, detail="You do not have permission to access this route")
        jds = []
        for x in jd_records.find({"r_id": r_id}, {"jd":1, "weights":1, "job_title":1, 'status':1}):
            x['_id'] = str(x['_id'])
            jds.append(x)		
        return JSONResponse(content={'data':jds}, status_code=200)				    		
    else:
        raise HTTPException(status_code=404, detail="Recruiter not found")

@app.get('/job/{j_id}')
async def get_job(j_id: str, current_user: str = Depends(get_current_user)):
    try:        
        job_details = jd_records.find_one({"_id": ObjectId(j_id)}, {'_id':0, "r_id": 1, "jd": 1, "weights": 1, "job_title": 1, "status": 1 })		
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid Job id")    
    if job_details is None:
        raise HTTPException(status_code=404, detail="Job id Not Found") 
    rec_details = employer_records.find_one({"_id": ObjectId(job_details["r_id"])})
    if current_user != rec_details["email"]:
        raise HTTPException(status_code=403, detail="You do not have permission to access this job")
    applicant_details = []
    for x in applicant_records.find({"j_id": j_id}, {'j_id':0, '_id':0}):        
        applicant_details.append(x)    
    job_details['candidates'] = applicant_details
    return JSONResponse(content={'data':job_details}, status_code=200)

@app.delete('/job/{j_id}')
async def delete_job(j_id: str, current_user: str = Depends(get_current_user)):
	try:        
		job_details = jd_records.find_one({"_id": ObjectId(j_id)}, {})		
	except Exception as e:
		raise HTTPException(status_code=404, detail="Invalid Job id")    
	if job_details:
		rec_details = employer_records.find_one({"_id": ObjectId(job_details["r_id"])})
		if current_user != rec_details["email"]:    	
			raise HTTPException(status_code=403, detail="You do not have permission to access this job")
		jd_records.delete_one({"_id": ObjectId(j_id)})		
	return Response(status_code=204)

@app.put('/job/{j_id}')
async def update_job(j_id: str, job_data: JobDetails, current_user: str = Depends(get_current_user)):
    job_data = job_data.dict()
    try:
        job_details = jd_records.find_one({"_id": ObjectId(j_id)})		
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid Job id")                 
    if not job_details:
        raise HTTPException(status_code=404, detail="Job not found")
    rec_details = employer_records.find_one({"_id": ObjectId(job_details["r_id"])})
    if current_user != rec_details["email"]: 	
        raise HTTPException(status_code=403, detail="You do not have permission to access this job")			
    jd_records.update_one({"_id": ObjectId(j_id)}, {"$set": job_data})		
    return Response(status_code=204)

if __name__ == '__main__':
    uvicorn.run('recruiter_backend:app', host='0.0.0.0', port=5001, reload=True)