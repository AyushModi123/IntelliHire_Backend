from fastapi import APIRouter, Depends
from auth import get_current_user
from models.jobs import JobsModel
from models.users import UsersModel, ApplicantsModel, EmployersModel, ReportsModel, ApplicantJobsModel
from models.questions import JobFitQuestionModel, AptitudeQuestionModel
from fastapi.responses import JSONResponse, Response, RedirectResponse
from fastapi import HTTPException, Depends
from db import Session, get_db
from schemas import JobFitScoreSchema, AptitudeScoreSchema, SkillScoreSchema
from sqlalchemy import func
from . import logging, logger

router = APIRouter(prefix="/job/{job_id}/assessment", tags=["Assessment"])
number_of_aptitude_questions = 15  

@router.get("")
async def assessment(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job or job.status == 'inactive':
            raise HTTPException(status_code=404, detail="Invalid Job ID")  
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
        if not applicant_job:
            return RedirectResponse(url=f"/job/{job_id}/apply")
        applicant_job = applicant_job.as_dict()
        del applicant_job["id"]
        del applicant_job["applicant_id"]
        del applicant_job["report_id"]        
        return JSONResponse(content={'data': applicant_job})
    raise HTTPException(status_code=403)

@router.get("/job-fit")
async def job_fit(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if current_user.role == "applicant":
            job = db.query(JobsModel).filter_by(id=job_id).first()
            if not job or job.status == 'inactive':
                raise HTTPException(status_code=404, detail="Invalid Job ID")  
            applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
            applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
            if not applicant_job:
                return RedirectResponse(url=f"/job/{job_id}/apply")
            if applicant_job.job_fit:
                return Response(status_code=400, content="Already Completed")
            job_fit_questions_model = db.query(JobFitQuestionModel).filter_by(job_id=job_id).all()
            job_fit_questions = []
            for job_fit_question_model in job_fit_questions_model:
                job_fit_question_dict = job_fit_question_model.as_dict()
                del job_fit_question_dict["answer"]
                job_fit_questions.append(job_fit_question_dict)
            # applicant_job.job_fit = True
            db.commit()
            return JSONResponse(content={"data": job_fit_questions})
        raise HTTPException(status_code=403)
    except Exception as e:
        db.rollback()
        logging.exception("Exception Occured")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/job-fit")
async def job_fit(data: JobFitScoreSchema, job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        try:
            job = db.query(JobsModel).filter_by(id=job_id).first()
            if not job or job.status == 'inactive':
                raise HTTPException(status_code=404, detail="Invalid Job ID")  
            applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
            applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
            if not applicant_job:
                return RedirectResponse(url=f"/job/{job_id}/apply")
            if not applicant_job.job_fit:
                return Response(status_code=400, content="First give assessment")
            report = db.query(ReportsModel).filter_by(job_id=job_id, applicant_id=applicant.id).first()
            if report:
                return Response(status_code=400, content="Already Completed")
            is_passed = True
            for answer in data.answers:
                job_fit_question = db.query(JobFitQuestionModel).filter_by(id=answer.id, answer=answer.answer_index).first()
                if not job_fit_question:
                    is_passed = False
                    break
            report = ReportsModel(
                job_fit_score=is_passed,
                job_id=job_id,
                applicant_id=applicant.id
            )
            db.add(report)
            db.commit()
        except Exception as e:
            db.rollback()
            logging.exception("Exception occurred")
            raise HTTPException(status_code=500)
    return Response(status_code=403)   
 
@router.get("/aptitude")
async def get_aptitude(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job or job.status == 'inactive':
            raise HTTPException(status_code=404, detail="Invalid Job ID")  
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
        if not applicant_job:
            return RedirectResponse(url=f"/job/{job_id}/apply")
        if not applicant_job.job_fit:
            return Response(status_code=400, content= "Complete Previous Stages First")
        if applicant_job.aptitude:
            return Response(status_code=400, content= "Already Completed")
        difficulty = job.aptitude_difficulty      
        aptitude_questions_model = (
                    db.query(AptitudeQuestionModel)
                    .filter_by(difficulty=difficulty)
                    .order_by(func.random())
                    .limit(number_of_aptitude_questions)
                    .all()
                )
        aptitude_questions = []
        for aptitude_question_model in aptitude_questions_model:
            aptitude_question_dict = aptitude_question_model.as_dict()
            del aptitude_question_dict["answer"]
            aptitude_questions.append(aptitude_question_dict)
        applicant_job.aptitude=True
        db.commit()
        return JSONResponse(content={"data": aptitude_questions})
    raise HTTPException(status_code=403)

@router.post("/aptitude")
async def aptitude(data: AptitudeScoreSchema, job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        try:
            job = db.query(JobsModel).filter_by(id=job_id).first()
            if not job or job.status == 'inactive':
                raise HTTPException(status_code=404, detail="Invalid Job ID")  
            applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
            applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
            if not applicant_job:
                return RedirectResponse(url=f"/job/{job_id}/apply")
            if not applicant_job.aptitude:
                return Response(status_code=400, content= "First give assessment")
            report = db.query(ReportsModel).filter_by(job_id=job_id, applicant_id=applicant.id).first()
            if not report:
                return Response(status_code=400, content= "Complete Previous Stages First")
            score = 0
            for answer in data.answers:
                job_fit_question = db.query(JobFitQuestionModel).filter_by(id=answer.id, answer=answer.answer_index).first()
                if job_fit_question:
                    score+=1
            report.aptitude_score = (score/number_of_aptitude_questions)*100
            db.commit()
        except Exception as e:
            db.rollback()
            logging.exception("Exception occurred")
            raise HTTPException(status_code=500)

@router.get("/skill")
async def get_skill(job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        job = db.query(JobsModel).filter_by(id=job_id).first()
        if not job or job.status == 'inactive':
            raise HTTPException(status_code=404, detail="Invalid Job ID")  
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
        applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
        if not applicant_job:
            return RedirectResponse(url=f"/job/{job_id}/apply")
        if not applicant_job.aptitude:
            return Response(status_code=400, content= "Complete Previous Stages First")
        if applicant_job.skill:
            return Response(status_code=400, content= "Already Completed")
        applicant_job.skill = True
        applicant_job.completed = True
        db.commit()
        #TO BE IMPLEMENTED
        return JSONResponse(content={"data": "TO BE IMPLEMENTED"})
    raise HTTPException(status_code=403)

#TO BE IMPLEMENTED
@router.post("/skill")
async def skill(data: SkillScoreSchema, job_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "applicant":
        try:
            job = db.query(JobsModel).filter_by(id=job_id).first()
            if not job or job.status == 'inactive':
                raise HTTPException(status_code=404, detail="Invalid Job ID")  
            applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
            applicant_job = db.query(ApplicantJobsModel).filter_by(applicant_id=applicant.id, job_id=job_id).first()
            if not applicant_job:
                return RedirectResponse(url=f"/job/{job_id}/apply")
            if not applicant_job.skill:
                return Response(status_code=400, content= "First give assessment")
            report = db.query(ReportsModel).filter_by(job_id=job_id, applicant_id=applicant.id).first()
            if not report:
                return Response(status_code=400, content= "Complete Previous Stages First")
            report.skill_score = 0
            db.commit()
        except Exception as e:
            db.rollback()
            logging.exception("Exception occurred")
            raise HTTPException(status_code=500)
    raise HTTPException(status_code=403)