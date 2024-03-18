import os
import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import APIRouter
from db import get_db, Session
from models.users import UsersModel
import bcrypt
from fastapi.responses import JSONResponse

router = APIRouter(tags=["auth"])


JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = db.query(UsersModel).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=403, detail="You do not have permission to access this job")    
    return user

@router.post("/token")
async def auth(user_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    email = user_data.username
    password = user_data.password    
    user = db.query(UsersModel).filter_by(email=email).first()
    if user:        
        email_val = user.email
        password_val = user.password
        role = user.role
        if bcrypt.checkpw(password.encode('utf-8'), password_val.encode('utf-8')):
            access_token = create_access_token({"sub": email})
            return JSONResponse(content={'access_token': access_token, 'role': role}, status_code=200)    
    raise HTTPException(status_code=401, detail="Email or Password do not match.")
