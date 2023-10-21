from fastapi import APIRouter
from fastapi import HTTPException, Depends
from models import JobDetails
from fastapi.responses import JSONResponse, Response
from bson import ObjectId
from db import employer_records, jd_records
from auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.post('/{r_id}')
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
    
@router.get('/{r_id}')
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