from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import json
from pymongo import MongoClient
import asyncio
from utils import scrape, data_cleaning
from utils import data_extraction
import threading
import multiprocessing
import os
import sys
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from waitress import serve

load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

