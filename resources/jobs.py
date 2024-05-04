from fastapi import APIRouter
from fastapi import HTTPException, Depends
from bson import ObjectId
from schemas import JobDetailsSchema
from auth import get_current_user
from fastapi.responses import JSONResponse, Response, RedirectResponse
from db import get_db, Session
from models.jobs import JobsModel
from models.users import UsersModel, ApplicantsModel, EmployersModel, ReportsModel, ApplicantJobsModel
from models.questions import JobFitQuestionModel, AptitudeQuestionModel
from utils import ranker
from . import logging, logger

router = APIRouter(tags=["Jobs/Create-Job"])

@router.post('/create-job')
async def post_job(job_data: JobDetailsSchema, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):    
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        data = job_data.dict()
        try:
            job_model = JobsModel(
                description=data.get("description"),
                weights=data.get("weights"),
                title=data.get("title"),
                status=data.get("status"),
                is_job_fit=data.get("is_job_fit"),
                is_aptitude=data.get("is_aptitude"),
                is_skill=data.get("is_skill"),
                aptitude_difficulty=data.get("aptitude_difficulty"),
                skill_difficulty=data.get("skill_difficulty"),
                employer_id=current_user.id
            )
            db.add(job_model)
            db.flush()  
            if data.get("is_job_fit"):              
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
            logging.exception("Exception occurred")
            raise HTTPException(status_code=500, detail=f"Internal Server Error")
        job = db.query(JobsModel).filter_by(id=job_model.id).first()
        job = job.as_dict()
        return JSONResponse(content={"job": job}, status_code=201)		
    raise HTTPException(status_code=403)

@router.get('/jobs')
async def get_jobs(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):    
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
            report_status = None
            report_score = None
            if report:
                report_status = report.status
                report_score = report.score
            jds.append({"id": job.id, "title": job.title, 'job_status': job.status, "candidate_status": report_status, "score": report_score})
        return JSONResponse(content={'data':jds}, status_code=200)
    raise HTTPException(status_code=403)

@router.get('/job/{job_id}')
async def get_job(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):       
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job or job.status == 'inactive':
            raise HTTPException(status_code=404, detail="Invalid Job ID")  
        job_applicants = []
        # To be implemented                
        job_description = job.description
        for applicant_job in db.query(ApplicantJobsModel).filter_by(job_id=job.id).all():            
            applicant = db.query(ApplicantsModel).filter_by(id=applicant_job.applicant_id).first()
            user_details = db.query(UsersModel).filter_by(id=applicant.user_id).first()
            report = db.query(ReportsModel).filter_by(id=applicant_job.report_id).first()
            applicant = applicant.as_dict()
            del applicant["user_id"]
            resume_text = applicant["resume_text"]
            score = ranker.score_resume(resume_text, job_description)            
            applicant["score"] = round((score + report.aptitude_score + report.skill_score)/3, 2)
            applicant["name"] = user_details.name
            applicant["email"] = user_details.email            
            job_applicants.append(applicant)
        job = job.as_dict()
        job['applicants'] = job_applicants   
        del job["employer_id"]
        return JSONResponse(content={'data':job}, status_code=200)
    elif current_user.role == "employer":
        return RedirectResponse(url=f"/job/{job_id}", status_code=308)
    raise HTTPException(status_code=403)

@router.delete('/job/{job_id}')
async def delete_job(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "employer":
        current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
        job = db.query(JobsModel).filter_by(id=job_id, employer_id=current_user.id).first()    
        if not job:
            raise HTTPException(status_code=404, detail="Invalid Job ID")                
        job.status = 'inactive'
        db.commit()
        return Response(status_code=200)
    return Response(status_code=403)

# @router.put('/job/{job_id}')
# async def update_job(job_id: str, job_data: JobDetailsSchema, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
#     if current_user.role == "employer":
#         current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
#         job_data = job_data.dict()
#         job = db.query(JobsModel).filter_by(id=job_id).first()
#         if not job or job.status == 'inactive':
#             raise HTTPException(status_code=404, detail="Invalid Job ID")  
#         job_fit_questions = db.query(JobFitQuestionModel).filter_by(job_id=job_id)
#         try:
#             if job_fit_questions.first():
#                 job_fit_questions.delete()
#                 db.flush()
#             for question in job_data.get("quiz_questions"):
#                     current_question = question.get("question")
#                     options = question.get("quiz_question_options")
#                     current_options = ""
#                     answer_index = 0
#                     for i, option in enumerate(options):
#                         current_options+=option.get("option")
#                         current_options+=";;;"
#                         if option.get("answer"):
#                             answer_index = i
#                     question_model = JobFitQuestionModel(
#                                 question=current_question,
#                                 choices=current_options,
#                                 answer=answer_index,
#                                 job_id=job_id
#                             )
#                     db.add(question_model)
#             del job_data["quiz_questions"]
#             job.update(job_data)
#             db.commit()
#         except Exception as e:
#             db.rollback()
#             logging.exception("Exception occurred")
#             raise HTTPException(status_code=500)
#         return Response(status_code=204)
    # raise HTTPException(status_code=403)

@router.get('/job/{job_id}/apply')
async def get_apply_job(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == 'applicant':
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job or job.status == 'inactive':
            raise HTTPException(status_code=404, detail="Invalid Job ID")        
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()        
        if not applicant_job:
            return JSONResponse(content={"data": {"resume": applicant.resume, "job_title": job.title, "job_description": job.description}})
        if applicant_job.completed:
            return JSONResponse(content={"redirect_url": f"/job/{job_id}/result"}, status_code=307)
        else:
            return JSONResponse(content={"redirect_url": f"/job/{job_id}/assessment"}, status_code=307)        
    raise HTTPException(status_code=403)

@router.post('/job/{job_id}/apply')
async def post_apply_job(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == 'applicant':
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job or job.status == 'inactive':
            raise HTTPException(status_code=404, detail="Invalid Job ID")          
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
        if applicant_job:
            raise HTTPException(status_code=409, detail="Already Applied")
        if not applicant.resume:
            raise HTTPException(status_code=404, detail="Resume Not Found")
        try:
            report_model = ReportsModel(
                job_fit_score=not job.is_job_fit,
                job_id=job_id,
                applicant_id=applicant.id
            )
            db.add(report_model)
            db.flush()
            applicant_job = ApplicantJobsModel(
                applicant_id=applicant.id,
                job_id=job_id,
                job_fit=not job.is_job_fit,
                aptitude=not job.is_aptitude,
                skill=not job.is_skill,
                report_id=report_model.id,
                resume=applicant.resume,
            )
            db.add(applicant_job)
            db.commit()
        except Exception as e:            
            db.rollback()
            logging.exception("Exception occurred")
            raise HTTPException(status_code=500)
        return Response(status_code=201)
    raise HTTPException(status_code=403)


@router.get("/job/{job_id}/result")
async def job_result(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job:            
            raise HTTPException(status_code=404, detail="Invalid Job ID")
        jds = []
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()#When Applicant completes application, it should get saved in applicants table
        applicant_job = db.query(ApplicantJobsModel).filter_by(job_id=job_id, applicant_id=applicant.id).first()        
        if not applicant_job:                        
            return JSONResponse(content={"redirect_url": f"/job/{job_id}"}, status_code=307)
        else:
            if not applicant_job.completed:
                return JSONResponse(content={"redirect_url": f"/job/{job_id}/assessment"}, status_code=307)
            report = db.query(ReportsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
            jds.append({"id": job.id, "description": job.description, "title": job.title, 'job_status': job.status, "candidate_status": report.status, "score": report.score})
            return JSONResponse(content={'data':jds}, status_code=200)
    raise HTTPException(status_code=403)
            