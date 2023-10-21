from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from db import engine
from models import Base
from resources import DashboardRouter, JobRouter, UserRouter
from auth import router as auth_router

app = FastAPI()

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(UserRouter)
app.include_router(DashboardRouter)
app.include_router(JobRouter)
app.include_router(auth_router)

if __name__ == '__main__':
    uvicorn.run('recruiter_backend:app', host='0.0.0.0', port=5001, reload=True)