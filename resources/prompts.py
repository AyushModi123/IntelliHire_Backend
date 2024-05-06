from fastapi import APIRouter
from fastapi import HTTPException, Depends
from schemas import JobDescriptionSchema, JobFitSchema
from auth import get_current_user
from fastapi.responses import JSONResponse, Response
from db import get_db, Session
from . import logging, logger
from models.users import EmployersModel
from prompts import job_description_prompt, JobDescriptionPromptsSchema, job_fit_prompt, JobFitQuestionsPromptsSchema
from utils.prompter import exec_prompt

async def is_premium(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):    
    current_user = db.query(EmployersModel).filter_by(user_id=current_user.id).first()
    if current_user:
        if not current_user.is_premium:
            raise HTTPException(status_code=403, detail="User does not have premium access")
        return current_user
    raise HTTPException(status_code=404, detail="User does not have access to this route")

router = APIRouter(prefix="/prompt", tags=["prompts"])


@router.post("/job-description")
async def job_description(data: JobDescriptionSchema, current_user: str = Depends(is_premium)):
    job_description = exec_prompt(output_schema=JobDescriptionPromptsSchema, parse_prompt=job_description_prompt, input_data={"company_name": current_user.company_name, "job_title": data.job_title, "domain": data.domain , "tone": data.tone})
    return JSONResponse(content={"job_description": job_description.content})
    # return JSONResponse(content={"job_description": "**Python Developer at Intellihire**\n\n**Job Description:**\n\nIntellihire, a leading IT solutions provider, is seeking a skilled Python Developer to join our dynamic team. As a Python Developer at Intellihire, you will be at the forefront of designing, developing, and implementing high-quality software solutions that meet the evolving needs of our clients. We are looking for a passionate individual who is eager to drive innovation and contribute to our mission of delivering excellence in the IT domain.\n\n**Key Responsibilities:**\n\n- Develop and maintain scalable and robust Python applications.\n- Collaborate with cross-functional teams to define, design, and ship new features.\n- Write clean, maintainable, and efficient code.\n- Troubleshoot, test, and maintain the core product software to ensure strong optimization and functionality.\n- Contribute to all phases of the development lifecycle.\n- Follow best practices (test-driven development, continuous integration, SCRUM, refactoring, code standards).\n- Stay informed about emerging technologies and software trends.\n\n**Qualifications:**\n\n- Bachelor's or Master's degree in Computer Science, Engineering, or a related field.\n- Proven experience as a Python Developer or similar role.\n- Expertise in at least one popular Python framework (like Django, Flask, or Pyramid).\n- Knowledge of object-relational mapping (ORM).\n- Familiarity with front-end technologies (like JavaScript and HTML5).\n- Understanding of databases and SQL.\n- Proficiency in version control tools and a good understanding of code versioning tools, such as Git.\n- Experience with development of RESTful APIs.\n\n**Desired Attributes and Skills:**\n\n- Strong analytical and problem-solving skills.\n- Excellent communication and teamwork abilities.\n- A keen eye for detail and a commitment to quality.\n- Ability to manage multiple projects simultaneously and meet deadlines.\n- Passion for writing clean, readable, and easily maintainable code.\n- Experience with cloud services (AWS, Google Cloud, etc.) and containerization technologies (Docker, Kubernetes) is a plus.\n\nJoin Intellihire and be a part of a team that values innovation, quality, and a collaborative work environment. If you are a motivated Python Developer looking for your next challenge, we would like to meet you. Apply now to embark on a rewarding career path where you can make a significant impact in the IT industry."})

@router.post("/job-fit")
async def job_fit(data: JobFitSchema, current_user: str = Depends(is_premium)):
    job_fit_questions = exec_prompt(output_schema=JobFitQuestionsPromptsSchema, parse_prompt=job_fit_prompt, input_data={"job_description": data.job_description, "company_desc": current_user.company_desc, "exclude_ques": data.exclude_ques})
    job_fit_questions = job_fit_questions.json()
    return JSONResponse(content={"data": job_fit_questions})