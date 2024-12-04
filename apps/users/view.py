
from fastapi import APIRouter

import base64
from fastapi import APIRouter, HTTPException, Depends,status,UploadFile,File
from sqlalchemy.orm import Session

from apps.users import models,schemas,utils
from apps.users.models import User,Document
# from .utils import hash_password
from fastapi.responses import JSONResponse
from core.database import get_db
from apps.users.utils import verify_password ,create_access_token,create_refresh_token,decode_access_token

router = APIRouter()
from apps.users.utils import get_current_user
from datetime import datetime
from typing import List

@router.post("/register",response_model=schemas.UserResponse)
def register_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists in the database
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return JSONResponse(
            content={"msg": "Email already registered", "user": existing_user.email}, 
            status_code=400
        )
  
    # Hash the user's password before storing
    hashed_password = utils.hash_password(request.password)
 
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        signature =request.signature

    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(
        content={"msg": "User successfully registered"}, 
        status_code=201
    )
  


@router.post("/token/refresh", response_model=dict)
def refresh_access_token(refresh_token: str):
    """Refresh the access token using a valid refresh token."""
    try:
        # Decode the refresh token
        payload = decode_access_token(refresh_token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Generate a new access token
        new_access_token = create_access_token(data={"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )



@router.post("/login", response_model=dict)
def user_login(request: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return a JWT token."""
    # Fetch the user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify the password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong  password",
        )

    # Generate a JWT token
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return JSONResponse({"access_token": access_token, "token_type": "bearer","refresh_token": refresh_token,})



@router.post("/upload_document/")
async def upload_document(
    file: UploadFile = File(...),  # The uploaded file
    userId: int = Depends(get_current_user),  # Get the current user (replace this with your logic)
    db: Session = Depends(get_db),  # Database session
):
    # Ensure the file is a PDF
    
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read the file content as binary data
    file_content = await file.read()
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    document = Document(
        title=file.filename,  # You can use a custom naming convention
        userId=userId.id,  # Associate the document with the user
          # You can customize the title as needed
        file_data=encoded_content , # Store the binary file content
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {"message": f"Document '{file.filename}' uploaded successfully!", "document_id": document.id}


@router.get("/user_document/", response_model=List[schemas.UserDocuments])
async def get_user_document(
    userId: int = Depends(get_current_user),  # Get the current user from OAuth token or other method
    db: Session = Depends(get_db),  # Database session dependency
):
    # Fetch documents for the given userId
    documents = db.query(models.Document).filter(models.Document.userId == userId.id).all()
    
    if not documents:
        raise HTTPException(status_code=404, detail="Documents not found for the user")

    return documents


@router.get("/hii")
def hi_root(user:Session=Depends(get_current_user)):
    # Assuming `db` is the user model instance with `id` attribute
    print(f"User ID: {user.email}")
    return {"hi": "how are yiu "}


@router.get("/bye")
def by_root():  
    return {"by": "Goodby "}