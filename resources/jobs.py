from fastapi import APIRouter
from fastapi import HTTPException, Depends
from bson import ObjectId
from schemas import JobDetailsSchema
from auth import get_current_user
from fastapi.responses import JSONResponse, Response, RedirectResponse
from db import db
from models.jobs import JobsModel
from models.users import UsersModel, ApplicantsModel, EmployersModel, ReportsModel, ApplicantJobsModel
from models.questions import JobFitQuestionModel, AptitudeQuestionModel
router = APIRouter(tags=["Jobs/Create-Job"])

@router.post('/create-job')
async def post_job(job_data: JobDetailsSchema, current_user: str = Depends(get_current_user)):    
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        data = job_data.dict()
        try:
            job_model = JobsModel(
                description=data.get("description"),
                weights=data.get("weights"),
                title=data.get("title"),
                status=data.get("status"),
                aptitude_difficulty=data.get("aptitude_difficulty"),
                skill_difficulty=data.get("skill_difficulty"),
                employer_id=current_user.id
            )
            db.add(job_model)
            db.flush()  
            for question in data.get("quiz_questions"):
                current_question = question.get("question")
                options = question.get("quiz_question_options")
                current_options = ""
                answer_index = 0
                for i, option in enumerate(options):
                    current_options+=option.get("option")
                    current_options+=";;;"
                    if option.get("answer"):
                        answer_index = i
                question_model = JobFitQuestionModel(
                            question=current_question,
                            choices=current_options,
                            answer=answer_index,
                            job_id=job_model.id
                        )
                db.add(question_model)
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
            raise HTTPException(status_code=500, detail=f"Internal Server Error")
        job = db.query(JobsModel).filter_by(id=job_model.id).first()
        job = job.as_dict()
        return JSONResponse(content={"job": job}, status_code=201)		
    return Response(status_code=403)

@router.get('/jobs')
async def get_jobs(current_user: str = Depends(get_current_user)):    
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        jds = []
        for job in db.query(JobsModel).filter_by(employer_id=current_user.id).all():
            jds.append({"id": job.id, "title": job.title, 'status': job.status})        
        return JSONResponse(content={'data':jds}, status_code=200)
    elif current_user.role == "applicant":
        current_user = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        jds = []
        applicant_jobs = db.query(ApplicantJobsModel).filter_by(applicant_id=current_user.id).all()
        for applicant_job in applicant_jobs:
            job = db.query(JobsModel).filter_by(id=applicant_job.job_id).first()
            report = db.query(ReportsModel).filter_by(id=applicant_job.report_id).first()
            jds.append({"id": job.id, "title": job.title, 'job_status': job.status, "candidate_status": report.status, "score": report.score})
        return JSONResponse(content={'data':jds}, status_code=200)
    raise HTTPException(status_code=403)

@router.get('/job/{job_id}')
async def get_job(job_id: str, current_user: str = Depends(get_current_user)):       
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        job = db.query(JobsModel).filter_by(id=job_id, employer_id=current_user.id).first()
        if not job:            
            raise HTTPException(status_code=404, detail="Invalid Job ID")
        job_applicants = []
        # To be implemented
        rank_counter = 1
        for applicant_job in db.query(ApplicantJobsModel).filter_by(job_id=job.id).all():            
            applicant = db.query(ApplicantsModel).filter_by(id=applicant_job.applicant_id).first()
            user_details = db.query(UsersModel).filter_by(id=applicant.user_id).first()
            applicant = applicant.as_dict()
            del applicant["user_id"]
            applicant["rank"] = rank_counter
            applicant["name"] = user_details.name
            applicant["email"] = user_details.email
            rank_counter+=1
            job_applicants.append(applicant)
        job = job.as_dict()
        job['applicants'] = job_applicants   
        del job["employer_id"]
        return JSONResponse(content={'data':job}, status_code=200)
    elif current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job:            
            raise HTTPException(status_code=404, detail="Invalid Job ID")
        jds = []
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()#When Applicant completes application, it should get saved in applicants table
        applicant_job = db.query(ApplicantJobsModel).filter_by(job_id=job_id, applicant_id=applicant.id).first()        
        if not applicant_job:                        
            return RedirectResponse(url=f"/job/{job_id}/assessment")
        else:
            report = db.query(ReportsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
            jds.append({"id": job.id, "description": job.description, "title": job.title, 'job_status': job.status, "candidate_status": report.status, "score": report.score})
            return JSONResponse(content={'data':jds}, status_code=200)
    
    

# @router.delete('/job/{job_id}')
# async def delete_job(job_id: str, current_user: str = Depends(get_current_user)):
#     if current_user.role == "employer":
#         job = db.query(JobsModel).filter_by(id=job_id, user_id=current_user.id).first()    
#         if not job:
#             raise HTTPException(status_code=404, detail="Invalid Job ID")                
#         db.delete(job)
#         db.commit()
#         return Response(status_code=204)
#     return Response(status_code=403)

@router.put('/job/{job_id}')
async def update_job(job_id: str, job_data: JobDetailsSchema, current_user: str = Depends(get_current_user)):
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        job_data = job_data.dict()
        job = db.query(JobsModel).filter_by(id=job_id, employer_id=current_user.id)
        if not job.first():            
            raise HTTPException(status_code=404, detail="Invalid Job ID")         
        job.update(job_data)
        db.commit()
        return Response(status_code=204)
    return Response(status_code=403)