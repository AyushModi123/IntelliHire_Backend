from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, func, DateTime
from sqlalchemy.types import Enum, UUID
from sqlalchemy.orm import relationship
from . import Base

class UsersModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)    
    mob_no = Column(String(25))
    location = Column(String(255))
    password = Column(String(255))
    role = Column(Enum('employer', 'applicant'))
    created_at = Column(DateTime, default=func.now())
    
    applicant = relationship("ApplicantsModel", backref="user")
    employer = relationship("EmployersModel", backref="user")
    # job = relationship("JobsModel", back_populates="users")

    def as_dict(cls):        
        return {
            "name": cls.name,
            "email": cls.email,
            "mob_no": cls.mob_no,
            "location": cls.location            
        }

class ApplicantsModel(Base):
    __tablename__ = 'applicants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)      
    user_id = Column(Integer, ForeignKey('users.id'))
    resume = Column(Boolean, default=False)

    def as_dict(cls):
        return {
            "id": cls.id,
            "user_id": cls.user_id            
        }
    
class ApplicantJobsModel(Base):
    __tablename__ = 'applicant_jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey('applicants.id'))
    job_id = Column(String(36), ForeignKey('jobs.id'))    
    report_id = Column(Integer, ForeignKey('reports.id'))
    resume = Column(Boolean, default=False)
    job_fit = Column(Boolean, default=False)
    aptitude = Column(Boolean, default=False)
    skill = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)

    def as_dict(cls):
        return {
            'id': cls.id,
            'applicant_id': cls.applicant_id,
            'job_id': cls.job_id,
            'report_id': cls.report_id,
            'resume': cls.resume,
            'job_fit': cls.job_fit,
            'aptitude': cls.aptitude,
            'skill': cls.skill,
            'is_completed': cls.completed
        }

class EmployersModel(Base):
    __tablename__ = 'employers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255))
    is_premium = Column(Boolean, default=False)   
    user_id = Column(Integer, ForeignKey('users.id'))
    company_desc = Column(String(2000))

    def as_dict(cls):
        return {            
            "company_name": cls.company_name,
            "is_premium": cls.is_premium,
            "company_desc": cls.company_desc
        }


class ReportsModel(Base):
    __tablename__ = 'reports'   

    id = Column(Integer, primary_key=True, autoincrement=True)    
    score = Column(Float)
    status = Column(Enum('pending', 'interview', 'rejected'), default='pending')
    job_fit_score = Column(Boolean, default=False)  # passed or not
    aptitude_score = Column(Float, default=0.0) # in percentage
    skill_score = Column(Float, default=0.0) # in percentage
    job_id = Column(String(36), ForeignKey('jobs.id'))
    applicant_id = Column(Integer, ForeignKey('applicants.id'))

class LinksModel(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)  
    linkedin_link = Column(String(255))
    github_link = Column(String(255))
    leetcode_link = Column(String(255))
    codechef_link = Column(String(255))
    codeforces_link = Column(String(255))
    applicant_id = Column(Integer, ForeignKey("applicants.id"))        

    def to_dict(self):
        return {            
            "github_link": self.github_link,
            "linkedin_link": self.linkedin_link,
            "leetcode_link": self.leetcode_link,
            "codechef_link": self.codechef_link,
            "codeforces_link": self.codeforces_link
        }
    
class EducationModel(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    name = Column(String(255))
    stream = Column(String(255))
    score = Column(String(255))
    location = Column(String(255))
    graduation_year = Column(String(255))

    def to_dict(self):
        return {
            "name": self.name,
            "stream": self.stream,
            "score": self.score,
            "location": self.location,
            "graduation_year": self.graduation_year
        }

class ExperienceModel(Base):
    __tablename__ = 'experience'

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    company_name = Column(String(255))
    role = Column(String(255))
    role_desc = Column(String(2048))
    start_date = Column(String(255))
    end_date = Column(String(255))

    def to_dict(self):
        return {
            "company_name": self.company_name,
            "role": self.role,
            "role_desc": self.role_desc,
            "start_date": self.start_date,
            "end_date": self.end_date
        }

class SkillsModel(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    skills = Column(String(1024))
    coding_skills = Column(String(500))

    '''{'platform': 'leetcode',
        'rating': ,
        'problems_solved': 
        }

        {'platform': 'geeksforgeeks', 
        'problems_solved': }

        {'platform': 'codeforces',
        'problems_solved':,
        'max_rating': }

        {'platform': 'codechef',
        'max_rating': ,
        'problems_solved':}'''

    def to_dict(self):
        return {
            "skills": self.skills
        }