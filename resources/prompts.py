from fastapi import APIRouter
from fastapi import HTTPException, Depends
from schemas import JobDescriptionSchema
from auth import get_current_user
from fastapi.responses import JSONResponse, Response
from db import db
from prompts import job_description_prompt, JobDescriptionPromptsSchema
from utils.prompter import exec_prompt

async def is_premium(current_user: str = Depends(get_current_user)):
    if not current_user.is_premium:
        return HTTPException(status_code=403, detail="User does not have premium access")
    return current_user

router = APIRouter(prefix="/prompt", tags=["prompts"])


@router.post("/job-description")
async def job_description(data: JobDescriptionSchema, current_user: str = Depends(is_premium)):
    job_description = exec_prompt(output_schema=JobDescriptionPromptsSchema, parse_prompt=job_description_prompt, input_data={"job_title": data.job_title, "industry": data.industry , "tone": data.tone})
    return JSONResponse(content={"job_description": job_description.content})
