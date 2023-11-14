from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from typing import Optional, Sequence
from pydantic import BaseModel, Field

class CandidateDetailsSchema(BaseModel):
    name: str = Field(None, description="name of person")
    email: str = Field(None, description="email of person")
    contact: str = Field(None, description="contact number of person")
    location: str = Field(None, description="location of person")

class EducationSchema(BaseModel):
    name: str = Field(None, description="name of college or school")
    stream: str = Field(None, description="stream of education")
    score: int = Field(None, description="contains score in this institute")
    location: str = Field(None, description="Location of institute")
    graduation_year: int = Field(None, description="Graduation Year")

class ExperienceSchema(BaseModel):
    company_name: str = Field(None, description="name of company")
    role: str = Field(None, description="role of experience")
    role_desc: str = Field(None, description="max 250 words short description of role")
    start_date: str = Field(None, description="start month and year of experience e.g. 03/2020")
    end_date: str = Field(None, description="end month and year of experience e.g. 06/2020")

class ResumeSchema(BaseModel):
    """Parsing Resume"""
    details: CandidateDetailsSchema = Field(..., description="Contains details of person as dictionary")
    education: Sequence[EducationSchema] = Field(..., description="Contains list of different educations")
    experience: Sequence[ExperienceSchema] = Field(..., description="Contains list of different experiences")
    skills: str = Field(None, description="Contains technical and non technical skills separated by comma")

class EmailSchema(BaseModel):
    """Generate Email"""
    subject: str = Field(..., description="Generate a short precise subject of email")
    body: str = Field(..., description="Generate body of email describing details of resume and how they fit the job")


parse_resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template='''You are a world class algorithm for extracting information in structured formats. Use the given format to extract information from the following input: {resume_text}. 
          Tip: Make sure to answer in the correct format. Return value of fields as None if value not found.'''
)

job_description_prompt = PromptTemplate(
    input_variables=["job_title", "industry", "tone", "company_name"],
    template='''Generate a comprehensive job description for a {job_title} in the {industry} industry at company {company_name}. The tone should be {tone}, 
        and the description should include key responsibilities, qualifications, and any specific attributes or skills desired. Ensure that the language is engaging and tailored to attract suitable candidates.'''
)

class JobDescriptionPromptsSchema(BaseModel):
    """Generate Job Description"""
    content: str = Field(..., description="Job Description")
