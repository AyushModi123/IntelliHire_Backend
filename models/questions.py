from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, UUID
import uuid
from . import Base

class JobFitQuestionModel(Base):
    __tablename__ = 'job_fit_questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(5000))
    choices = Column(String(5000))  #Separate choices by ';;;'
    answer = Column(Integer) #Store correct choice's number    

    job_id = Column(String(36), ForeignKey('jobs.id'))


class AptitudeQuestionModel(Base):
    __tablename__ = 'aptitude_questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(5000))
    choices = Column(String(5000))  #Separate choices by ';;;'
    answer = Column(Integer) #Store correct choice's number
    difficulty = Column(Enum('easy', 'medium', 'hard'))