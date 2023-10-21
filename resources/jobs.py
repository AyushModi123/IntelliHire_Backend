from fastapi import APIRouter
from fastapi import HTTPException, Depends
from db import employer_records
from fastapi import HTTPException
from bson import ObjectId
from models import JobDetails
from auth import get_current_user
from fastapi.responses import JSONResponse, Response
from db import employer_records, applicant_records, jd_records
router = APIRouter(prefix="/job", tags=["Jobs"])

@router.get('/{j_id}')
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

@router.delete('/{j_id}')
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

@router.put('/{j_id}')
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