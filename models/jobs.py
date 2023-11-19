from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, UUID
import uuid
from . import Base

class JobsModel(Base):
    __tablename__ = 'jobs'
    
    id = Column(String(36), default=lambda: str(uuid.uuid4()), nullable=False, primary_key=True)
    description = Column(String(2000))
    weights = Column(String(1000))    
    title = Column(String(255))
    aptitude_difficulty = Column(Enum('easy', 'medium', 'hard', 'mix'))
    skill_difficulty = Column(Enum('easy', 'medium', 'hard', 'mix'))
    status = Column(Enum('active', 'inactive'), default='active')
    employer_id = Column(Integer, ForeignKey('employers.id'))
    # job = relationship("UsersModel", back_populates="jobs")
    # employer = relationship("ApplicantsModel", backref="jobs")
    
    def as_dict(cls):
        return {
            "id": cls.id,
            "description": cls.description,
            "weights": cls.weights,
            "title": cls.title,
            "status": cls.status,
            "employer_id": cls.employer_id,
            "aptitude_difficulty": cls.aptitude_difficulty,
            "skill_difficulty": cls.skill_difficulty
        }