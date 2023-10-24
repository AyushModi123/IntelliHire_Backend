from fastapi import APIRouter
from schemas import SignupSchema, UserLoginSchema
from db import db
from fastapi import HTTPException, Depends, UploadFile
import bcrypt
from models.users import UsersModel, ApplicantsModel, EmployersModel, LinksModel, SkillsModel, ExperienceModel, EducationModel
from utils import ResumeParser, exec_prompt
import io
from auth import create_access_token, get_current_user
from fastapi.responses import JSONResponse, Response
from typing import Union

router = APIRouter(tags=["Users/Resume"])

@router.post("/signup")
async def signup(user_data: SignupSchema):
    data = user_data.dict()
    role = data.get("role")
    email = data.get("email")      
    location = data.get("location")     
    user = db.query(UsersModel).filter_by(email=email).first()
    if user:
        raise HTTPException(status_code=400, detail="This email already exists in the database")
    else:
        if role == "employer":
            password = data.get("password1")            
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())            
            user_model = UsersModel(
                name=data.get("name"),
                email=email,
                mob_no=data.get("mob_no"),                               
                password=hashed_pass,
                role=role,
                location=location
            )
            db.add(user_model)
            employer_model= EmployersModel(
                company_name=data.get("company_name"), 
                user_id=user_model.id
            )
            db.add(employer_model)
            db.commit()             
        elif role == "applicant":
            password = data.get("password1")                     
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())            
            user_model = UsersModel(
                name=data.get("name"),
                email=email,
                mob_no=data.get("mob_no"),                               
                password=hashed_pass,
                role=role,
                location=location
            )
            db.add(user_model)
            # applicant_model = ApplicantsModel(
            #     user_id=user_model.id,
            #     job_id=data.get("job_id"),
            # )
            # db.add(applicant_model)
            db.commit()                         
        access_token = create_access_token({"sub": email})
        return JSONResponse(content={'access_token': access_token, 'role': role}, status_code=201)

@router.post("/login")
async def login(user_data: UserLoginSchema):
    email = user_data.email
    password = user_data.password    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user:        
        email_val = user.email
        password_val = user.password
        role = user.role        
        if bcrypt.checkpw(password.encode('utf-8'), password_val.encode('utf-8')):
            access_token = create_access_token({"sub": email_val})
            return JSONResponse(content={'access_token': access_token, 'role': role}, status_code=200)    
    raise HTTPException(status_code=401, detail="Email or Password do not match.")

@router.post("/upload_resume")
async def upload_resume(file: UploadFile, current_user: str = Depends(get_current_user)):
    current_user_id = current_user.id
    if file.content_type != "application/pdf":
        return HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_bytes = await file.read()
    de_obj = ResumeParser(io.BytesIO(file_bytes))
    linkedin_link, github_link, leetcode_link, codechef_link, codeforces_link = de_obj.get_profile_links()
    from utils import scrape, data_cleaning
    codingData = scrape((None, codeforces_link, codechef_link, leetcode_link))
    if len(codingData) > 0:
        cleaned_data = data_cleaning().clean_data(codingData)
        print(cleaned_data)
    doc = de_obj.parse_resume()    
    cand_details = doc.details
    user_details = LinksModel(
        user_id=current_user_id,        
        linkedin_link = linkedin_link,
        github_link = github_link,
        leetcode_link = leetcode_link,
        codechef_link = codechef_link,
        codeforces_link = codeforces_link
        )
    for ed in doc.education:
        education = EducationModel(
            user_id=current_user_id,
            name=ed.name,
            stream=ed.stream,
            score=ed.score,
            location=ed.location,
            graduation_year=ed.graduation_year
        )
    for exp in doc.experience:
        experience = ExperienceModel(
            user_id = current_user_id,
            company_name=exp.company_name,
            role=exp.role,
            role_desc=exp.role_desc,
            start_date=exp.start_date,
            end_date=exp.end_date
        )        
    skills = SkillsModel(
        user_id=current_user_id,
        skills=doc.skills
        )
    db.add(user_details)
    db.add(education)
    db.add(experience)
    db.add(skills)
    db.commit()
    return JSONResponse(content={'message': "PDF file uploaded and parsed successfully."}, status_code=201)