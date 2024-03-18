from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import os

SQLALCHEMY_DATABASE_URL =  os.getenv('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()