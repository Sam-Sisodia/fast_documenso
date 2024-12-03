
from fastapi import APIRouter




import base64
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from apps.users import models,schemas,utils
# from .utils import hash_password
from fastapi.responses import JSONResponse
from core.database import get_db

router = APIRouter()


@router.post("/register",response_model=schemas.UserResponse)
def register_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists in the database
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        return JSONResponse(
            content={"msg": "Email already registered", "user": existing_user.email}, 
            status_code=400
        )
  
    # Hash the user's password before storing
    hashed_password = utils.hash_password(request.password)
 
    new_user = models.User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(
        content={"msg": "User successfully registered"}, 
        status_code=201
    )
  
  






@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/hii")
def hi_root():
    return {"hi": "how are yiu "}


@router.get("/bye")
def by_root():  
    return {"by": "Goodby "}