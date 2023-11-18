from fastapi import APIRouter
from schemas import SignupSchema, UserLoginSchema
from db import db
from . import logging, logger
from fastapi import HTTPException, Depends, UploadFile
import bcrypt
from models.users import UsersModel, ApplicantsModel, EmployersModel, LinksModel, SkillsModel, ExperienceModel, EducationModel, ApplicantJobsModel
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
        name = data.get("name")
        if role == "employer":
            password = data.get("password1")            
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())            
            try:
                user_model = UsersModel(
                    name=name,
                    email=email,
                    mob_no=data.get("mob_no"),                               
                    password=hashed_pass,
                    role=role,
                    location=location
                )
                db.add(user_model)
                db.flush()                             
                employer_model= EmployersModel(
                    company_name=data.get("company_name"), 
                    user_id=user_model.id,
                    is_premium=data.get("is_premium"),
                    company_desc=data.get("company_desc")
                )
                db.add(employer_model)
                db.commit()             
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
        elif role == "applicant":
            password = data.get("password1")                     
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())            
            try:
                user_model = UsersModel(
                    name=name,
                    email=email,
                    mob_no=data.get("mob_no"),                               
                    password=hashed_pass,
                    role=role,
                    location=location
                )
                db.add(user_model)
                db.flush()
                applicant_model = ApplicantsModel(
                    user_id=user_model.id
                )
                db.add(applicant_model)
                db.commit()                         
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
        access_token = create_access_token({"sub": email})
        return JSONResponse(content={'access_token': access_token, 'name': name, 'role': role}, status_code=201)

@router.post("/login")
async def login(user_data: UserLoginSchema):
    email = user_data.email
    password = user_data.password    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user:        
        email_val = user.email
        password_val = user.password
        role = user.role  
        name = user.name
        if bcrypt.checkpw(password.encode('utf-8'), password_val.encode('utf-8')):
            access_token = create_access_token({"sub": email_val})
            return JSONResponse(content={'access_token': access_token, 'name': name, 'role': role}, status_code=200)    
    raise HTTPException(status_code=401, detail="Email or Password do not match.")

@router.post("/upload_resume")
async def upload_resume(file: UploadFile, current_user: str = Depends(get_current_user)):
    if current_user.role == "applicant":    
        applicant = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first()
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
        link = LinksModel(
            applicant_id=applicant.id,
            linkedin_link = linkedin_link,
            github_link = github_link,
            leetcode_link = leetcode_link,
            codechef_link = codechef_link,
            codeforces_link = codeforces_link
            )
        for ed in doc.education:
            education = EducationModel(
                applicant_id=applicant.id,
                name=ed.name,
                stream=ed.stream,
                score=ed.score,
                location=ed.location,
                graduation_year=ed.graduation_year
            )
        for exp in doc.experience:
            experience = ExperienceModel(
                applicant_id=applicant.id,
                company_name=exp.company_name,
                role=exp.role,
                role_desc=exp.role_desc,
                start_date=exp.start_date,
                end_date=exp.end_date
            )        
        skills = SkillsModel(
            applicant_id=applicant.id,
            skills=doc.skills
            )
        try:
            db.add(link)
            db.add(education)
            db.add(experience)
            db.add(skills)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return JSONResponse(content={'message': "PDF file uploaded and parsed successfully."}, status_code=201)
    raise HTTPException(status_code=403, detail="User does not have access to this route.")

@router.get("/details")
async def get_details(current_user: str = Depends(get_current_user)):    
    if current_user.role == "employer":
        employer_details = db.query(EmployersModel).filter_by(user_id=current_user.id).first().as_dict()
        employer_details = employer_details | {
            "name": current_user.name,
            "email": current_user.email,
            "mob_no": current_user.mob_no,
            "location": current_user.location            
        }        
        return JSONResponse(content={"data": employer_details})
    if current_user.role == "applicant":
        # applicant_details = db.query(ApplicantsModel).filter_by(user_id=current_user.id).first().as_dict()
        applicant_details = {
            "name": current_user.name,
            "email": current_user.email,
            "mob_no": current_user.mob_no,
            "location": current_user.location            
        }
        return JSONResponse(content={"data": applicant_details})
    raise HTTPException(status_code=403)