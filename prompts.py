from langchain import PromptTemplate
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from typing import Optional, Sequence, List
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
    input_variables=["job_title", "domain", "tone", "company_name"],
    template='''Generate a comprehensive job description for a {job_title} in the {domain} domain at company {company_name}. The tone should be {tone}, 
        and the description should include key responsibilities, qualifications, and any specific attributes or skills desired. Ensure that the language is engaging and tailored to attract suitable candidates.'''
)

class JobDescriptionPromptsSchema(BaseModel):
    """Generate Job Description"""
    content: str = Field(..., description="Job Description")

job_fit_prompt = PromptTemplate(
    input_variables=["job_description", "company_desc", "exclude_ques"],
    template='''Based on the given job_description: {job_description}
    ; company_description: {company_desc}.
    Generate 3 basic fit questions that an interviewer might ask candidates.
    These questions should focus on assessing the candidate's qualifications, experience, and educational background. Include questions similar to 'How many years of experience do you have?' and 'Do you have a [specific degree]?' to help evaluate the candidate's fitness for the role.
    Exclude these questions: {exclude_ques}'''
)

class JobFitOptionsPromptsSchema(BaseModel):
    id: int = Field(..., description="Option number")
    option: str = Field(..., description="Option Text")
    answer: bool = Field(..., description="Correct/Incorrect")

class JobFitQuestionPromptsSchema(BaseModel):
    question: str = Field(..., description="Question")
    quiz_question_options: List[JobFitOptionsPromptsSchema]

class JobFitQuestionsPromptsSchema(BaseModel):
    """Generate Job Fit Questions"""
    quiz_questions: List[JobFitQuestionPromptsSchema]