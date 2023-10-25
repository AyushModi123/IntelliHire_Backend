from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
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
    
    # applicant = relationship("ApplicantsModel", backref="users")
    # employer = relationship("EmployersModel", backref="users")
    # job = relationship("JobsModel", back_populates="users")

class ApplicantsModel(Base):
    __tablename__ = 'applicants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    job_id = Column(String(36), ForeignKey('jobs.id'))    

class EmployersModel(Base):
    __tablename__ = 'employers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255))    
    user_id = Column(Integer, ForeignKey('users.id'))


class ReportModel(Base):
    __tablename__ = 'reports'   

    id = Column(Integer, primary_key=True, autoincrement=True)    
    score = Column(Float)
    status = Column(Enum('pending', 'interview', 'rejected'), default='pending')
    achievements = Column(Integer)
    coding_profiles = Column(Integer) 
    education = Column(Integer)
    experience = Column(Integer)
    projects = Column(Integer)
    skills = Column(Integer)
    job_id = Column(String(36), ForeignKey('jobs.id'))
    user_id = Column(Integer, ForeignKey('applicants.id'))

class LinksModel(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))        
    linkedin_link = Column(String(255))
    github_link = Column(String(255))
    leetcode_link = Column(String(255))
    codechef_link = Column(String(255))
    codeforces_link = Column(String(255))

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
    user_id = Column(Integer, ForeignKey("users.id"))
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
    user_id = Column(Integer, ForeignKey("users.id"))
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
    user_id = Column(Integer, ForeignKey("users.id"))
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