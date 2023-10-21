from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, UUID
import uuid
from . import Base

class JobsModel(Base):
    __tablename__ = 'jobs'
    
    id = Column(String(36), default=str(uuid.uuid4()), nullable=False, primary_key=True)
    description = Column(String(2000))
    weights = Column(String(1000))    
    title = Column(String(255))
    status = Column(Enum('active', 'inactive'), default='active')
    user_id = Column(Integer, ForeignKey('users.id'))
    # job = relationship("UsersModel", back_populates="jobs")
    # employer = relationship("ApplicantsModel", backref="jobs")
    
    def as_dict(cls, job):
        return {
            "id": job.id,
            "description": job.description,
            "weights": job.weights,
            "title": job.title,
            "status": job.status,
            "user_id": job.user_id
        }