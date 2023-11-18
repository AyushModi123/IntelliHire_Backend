from fastapi import APIRouter, Depends
from auth import get_current_user
from models.jobs import JobsModel
from models.users import UsersModel, ApplicantsModel, EmployersModel, ReportsModel, ApplicantJobsModel
from fastapi.responses import JSONResponse, Response
from fastapi import HTTPException, Depends
from db import db

router = APIRouter(tags=["Assessment"])


@router.get("/job/{job_id}/assessment")
async def assessment(job_id: str, current_user: str = Depends(get_current_user)):
    if current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job:            
            raise HTTPException(status_code=404, detail="Invalid Job ID")        
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
        applicant_job = applicant_job.as_dict()
        del applicant_job["id"]
        del applicant_job["applicant_id"]
        return JSONResponse(content={'data': applicant_job})
    raise HTTPException(status_code=403)

