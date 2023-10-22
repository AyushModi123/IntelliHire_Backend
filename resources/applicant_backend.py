from fastapi import APIRouter, Depends
from auth import get_current_user

# router = APIRouter(prefix="/applicant", name="Applicants")


# @router.get("/assessment")
# async def assessment(current_user: str = Depends(get_current_user)):
#     pass
