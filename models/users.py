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
