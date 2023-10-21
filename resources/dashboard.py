from fastapi import APIRouter
from fastapi import HTTPException, Depends
from schemas import JobDetailsSchema
from models.jobs import JobsModel
from fastapi.responses import JSONResponse, Response
from bson import ObjectId
from db import db
from auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.post('')
async def post_job(job_data: JobDetailsSchema, current_user: str = Depends(get_current_user)):    
    data = job_data.dict()
    job_model = JobsModel(
        description=data.get("description"),
        weights="[" + ', '.join(map(str, data.get("weights"))) + "]",
        title=data.get("title"),
        status=data.get("status"),
        user_id=current_user.id
    )
    db.add(job_model)
    db.commit()    
    return JSONResponse(content={'j_id':job_model.id}, status_code=201)		
    
@router.get('')
async def get_jobs(current_user: str = Depends(get_current_user)):    
    jds = []
    for job in db.query(JobsModel).filter_by(user_id=current_user.id).all():
        jds.append({"id": job.id, "description": job.description, "weights": job.weights, "title": job.title, 'status': job.status})        
    return JSONResponse(content={'data':jds}, status_code=200)				    		#change weights type