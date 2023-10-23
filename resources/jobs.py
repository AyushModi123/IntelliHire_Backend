from fastapi import APIRouter
from fastapi import HTTPException, Depends
from bson import ObjectId
from schemas import JobDetailsSchema
from auth import get_current_user
from fastapi.responses import JSONResponse, Response
from db import db
from models.jobs import JobsModel
from models.users import UsersModel, ApplicantsModel, EmployersModel, ReportModel
router = APIRouter(prefix="/job", tags=["Jobs"])

@router.get('/{job_id}')
async def get_job(job_id: str, current_user: str = Depends(get_current_user)):            
    job = db.query(JobsModel).filter_by(id=job_id).first()
    if not job:            
        raise HTTPException(status_code=404, detail="Invalid Job ID") 
    job_applicants = []
    for applicant in db.query(ApplicantsModel).filter_by(job_id=job.id).all():
        job_applicants.append(applicant)    
    job = job.as_dict(job)
    job['applicants'] = job_applicants    
    return JSONResponse(content={'data':job}, status_code=200)

@router.delete('/{job_id}')
async def delete_job(job_id: str, current_user: str = Depends(get_current_user)):
    job = db.query(JobsModel).filter_by(id=job_id).first()    
    if not job:
        raise HTTPException(status_code=404, detail="Invalid Job ID")                
    db.delete(job)
    db.commit()
    return Response(status_code=204)

@router.put('/{job_id}')
async def update_job(job_id: str, job_data: JobDetailsSchema, current_user: str = Depends(get_current_user)):
    job_data = job_data.dict()
    job = db.query(JobsModel).filter_by(id=job_id)
    if not job.first():            
        raise HTTPException(status_code=404, detail="Invalid Job ID")         
    job.update(job_data)
    db.commit()
    return Response(status_code=204)