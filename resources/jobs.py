from fastapi import APIRouter
from fastapi import HTTPException, Depends
from bson import ObjectId
from schemas import JobDetailsSchema
from auth import get_current_user
from fastapi.responses import JSONResponse, Response
from db import db
from models.jobs import JobsModel
from models.users import UsersModel, ApplicantsModel, EmployersModel, ReportsModel
router = APIRouter(tags=["Jobs/Create-Job"])

@router.post('/create-job')
async def post_job(job_data: JobDetailsSchema, current_user: str = Depends(get_current_user)):    
    if current_user.role == "employer":
        data = job_data.dict()
        job_model = JobsModel(
            description=data.get("description"),
            weights=data.get("weights"),
            title=data.get("title"),
            status=data.get("status"),
            user_id=current_user.id
        )
        db.add(job_model)
        db.commit()    
        return JSONResponse(content={'j_id':job_model.id}, status_code=201)		
    return Response(status_code=403)

@router.get('/jobs')
async def get_jobs(current_user: str = Depends(get_current_user)):    
    if current_user.role == "employer":
        jds = []
        for job in db.query(JobsModel).filter_by(user_id=current_user.id).all():
            jds.append({"id": job.id, "title": job.title, 'status': job.status})        
        return JSONResponse(content={'data':jds}, status_code=200)
    elif current_user.role == "applicant":
        jds = []
        applicant_jobs = db.query(ApplicantsModel).filter_by(user_id=current_user.id).all()
        for applicant_job in applicant_jobs:
            job = db.query(JobsModel).filter_by(id=applicant_job.job_id).first()
            report = db.query(ReportsModel).filter_by(user_id=current_user.id, job_id=job.id).first()
            jds.append({"id": job.id, "title": job.title, 'job_status': job.status, "candidate_status": report.status, "score": report.score})
        return JSONResponse(content={'data':jds}, status_code=200)	

@router.get('/job/{job_id}')
async def get_job(job_id: str, current_user: str = Depends(get_current_user)):       
    if current_user.role == "employer":
        job = db.query(JobsModel).filter_by(id=job_id, user_id=current_user.id).first()
        if not job:            
            raise HTTPException(status_code=404, detail="Invalid Job ID")
        job_applicants = []
        # To be implemented 
        # for applicant in db.query(ApplicantsModel).filter_by(job_id=job.id).all():
        #     applicant.user_id
            # job_applicants.append(applicant)   
        job = job.as_dict(job)
        job['applicants'] = job_applicants   
        del job["user_id"]
        return JSONResponse(content={'data':job}, status_code=200)
    elif current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job:            
            raise HTTPException(status_code=404, detail="Invalid Job ID")
        jds = []
        user_job = db.query(ApplicantsModel).filter_by(user_id=current_user.id, job_id=job_id).first()#When Applicant completes application, it should get saved in applicants table
        if not user_job:            
            return Response(status_code=404)
        else:
            report = db.query(ReportsModel).filter_by(user_id=current_user.id, job_id=job.id).first()
            jds.append({"id": job.id, "description": job.description, "title": job.title, 'job_status': job.status, "candidate_status": report.status, "score": report.score})
            return JSONResponse(content={'data':jds}, status_code=200)
    
    

@router.delete('/job/{job_id}')
async def delete_job(job_id: str, current_user: str = Depends(get_current_user)):
    if current_user.role == "employer":
        job = db.query(JobsModel).filter_by(id=job_id, user_id=current_user.id).first()    
        if not job:
            raise HTTPException(status_code=404, detail="Invalid Job ID")                
        db.delete(job)
        db.commit()
        return Response(status_code=204)
    return Response(status_code=403)

@router.put('/job/{job_id}')
async def update_job(job_id: str, job_data: JobDetailsSchema, current_user: str = Depends(get_current_user)):
    if current_user.role == "employer":
        job_data = job_data.dict()
        job = db.query(JobsModel).filter_by(id=job_id, user_id=current_user.id)
        if not job.first():            
            raise HTTPException(status_code=404, detail="Invalid Job ID")         
        job.update(job_data)
        db.commit()
        return Response(status_code=204)
    return Response(status_code=403)