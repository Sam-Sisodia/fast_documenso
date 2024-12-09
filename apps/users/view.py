
from fastapi import APIRouter

import base64
from fastapi import APIRouter, HTTPException, Depends,status,UploadFile,File
from sqlalchemy.orm import Session

from apps.users import models,schemas,utils
from apps.users.models import User,Document,FieldType,Recipient,DocumentSharedLink,CheckFields
# from .utils import hash_password
from fastapi.responses import JSONResponse
from core.database import get_db
from sqlalchemy.exc import IntegrityError
from apps.users.utils import verify_password ,create_access_token,create_refresh_token,decode_access_token


from apps.users.utils import get_current_user,recipientsmail
from datetime import datetime
from typing import List
import uuid 
from sqlalchemy.orm import joinedload
router = APIRouter()
 
from apps.users.schemas import ActiveField

def ss(db: Session):
    nn = db.query(FieldType).all()  # Query FieldType table
    return nn



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
    return new_user
  


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
    return JSONResponse({"access_token": access_token, 
                         "token_type": "bearer",
                         "refresh_token": refresh_token,
                         "expire_time": utils.ACCESS_TOKEN_EXPIRE_MINUTES})



class DocumentManager:
    @router.post("/upload-document/")
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
            title=file.filename, 
            userId=userId.id,  
            file_data=encoded_content ,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return {"message": f"Document '{file.filename}' uploaded successfully!", "document_id": document.id}


    
    #get all document 
    @router.get("/user-documents/", response_model=List[schemas.UserDocuments])
    async def get_user_document(
        userId: int = Depends(get_current_user),  # Get the current user from OAuth token or other method
        db: Session = Depends(get_db)):
        documents = db.query(models.Document).filter(models.Document.userId == userId.id).all()
        if not documents:
            raise HTTPException(status_code=404, detail="Documents not found for the user")

        # return documents
        return documents

    #get single document 
    @router.get("/user-document/{id}", response_model=schemas.UserDocument)
    async def get_single_document(
        id: int,  # Path parameter to get the document id from the URL
        userId: int = Depends(get_current_user),  # Get the current user from OAuth token or other method
        db: Session = Depends(get_db)  # Database session dependency
    ):
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id  # Use the path parameter 'id'
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")
        document_data = schemas.UserDocument.from_orm(document)
        active_fields_query = db.query(models.CheckFields).filter(models.CheckFields.document_id==id,
                                                            models.CheckFields.inserted==True)
        
       
        active_fields = [
        ActiveField(
            id=field.id,
            name=field.name,
            status=True  # Assuming the status is always True for active fields
        )
        for ac in active_fields_query
        if (field := db.query(models.FieldType).filter(models.FieldType.id == ac.field_id).first())
    ]

        
        document_data.doc_fields = db.query(FieldType).all()  
        document_data.active_fileds = active_fields

        return document_data 
    
    

    
    @router.patch("/update-document/{id}", response_model=schemas.UserDocument)
    async def update_document(
        id: int,  # Path parameter to get the document id from the URL
        document_update: schemas.UserDocument,
        userId: int = Depends(get_current_user),  # Get the current user from OAuth token or other method
        db: Session = Depends(get_db),  # Database session dependency
       
    ):
        # Fetch the document to update
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")

        # Update fields with the new values
        document.title = document_update.title
        
        db.commit()  # Commit the changes to the database
        db.refresh(document)  # Refresh the session with the updated document

        return document  # Return the updated document
    

    # 
    @router.delete("/delete-document/{id}", response_model=schemas.UserDocument)
    async def delete_document(
        id: int,  # Path parameter for document ID
        userId: int = Depends(get_current_user),  # Get the current user from OAuth or another method
        db: Session = Depends(get_db)  # Database session dependency
    ):
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id
        ).first()

       
        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")

        # Delete the document
        db.delete(document)
        db.commit()

        # Return the deleted document's data as confirmation
        return  JSONResponse ({"message": "documnet delete sucessfully"})


    

class FieldTypeManager:
    @router.post("/add-fields", response_model=schemas.FieldsType)
    async def add_fields(request: schemas.FieldsType, userId: int = Depends(get_current_user), db: Session = Depends(get_db)):
        # Check if the field name already exists in the database
        existing_field = db.query(FieldType).filter(FieldType.name == request.name).first()
        if existing_field:
            raise HTTPException(
                status_code=400,
                detail=f"Field with name '{request.name}' already registered"
            )

        # Create the new FieldType entry
        field = FieldType(
            name=request.name,
            signature=request.signature,
            positionX=request.positionX,
            positionY=request.positionY,
            width=request.width,
            height=request.height
        )
        db.add(field)
        db.commit()
        db.refresh(field)

        # Return the newly created FieldType object
        return field
       
    @router.get("/get-fields")
    async def add_fields(userId: int = Depends(get_current_user),db: Session = Depends(get_db)):
        data = db.query(FieldType).all()
        return data
        
        



class RecipientManager:
    # @router.get("/user-recipients/", response_model=List[schemas.UserDocuments])
    # async def get_recipients(
    #     userId: int = Depends(get_current_user),  # Get the current user from OAuth token or other method
    #     db: Session = Depends(get_db)):
    #     #
    #     documents = db.query(models.Recipient).filter(models.Document.userId == userId.id).all()
        
    #     if not documents:
    #         raise HTTPException(status_code=404, detail="Documents not found for the user")

    #     # return documents
    #     return [schemas.UserDocuments.from_orm(doc) for doc in documents]




    @router.post("/assign-recipients")
    async def add_recipients(
        request: schemas.DocumentRecipientsRequest,
        userId: int = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        try:
    # Fetch the document to verify its existence
            document = db.query(Document).filter(Document.id == request.document_id).first()
            if not document:
                return {"error": "Document not found"}

            recipients = []
            for recipient_data in request.recipients:
                existing_recipient = db.query(Recipient).filter(
                    Recipient.email == recipient_data.email,
                    Recipient.document_id == request.document_id
                ).first()

                if not existing_recipient:
                    recipient = Recipient(
                        document_id=request.document_id,
                        name=recipient_data.name,
                        email=recipient_data.email,
                        role=recipient_data.role,
                    )
                    recipients.append(recipient)

            if recipients:
                db.add_all(recipients)
                db.flush()

                document_links = []
                for recipient in recipients:
                    shared_link = DocumentSharedLink(
                        token=str(uuid.uuid4()),
                        document_id=request.document_id,
                        recipient_id=recipient.id,
                    )
                    document_links.append(shared_link)

                db.add_all(document_links)
                db.flush()

            if request.fields:
                fields_to_add = []
                for field_id in request.fields:
                    document_field = CheckFields(
                        document_id=request.document_id,
                        field_id=field_id,
                        inserted=True,
                    )
                    fields_to_add.append(document_field)

                db.add_all(fields_to_add)
                db.flush()

            db.commit()

            if recipients:
                recipientsmail(document_links)

            return {"message": "Recipients and fields added successfully"}

        except IntegrityError as e:
            db.rollback()
            return {"error": "Failed to add recipients or fields", "details": str(e)}

        except Exception as e:
            db.rollback()
            return {"error": "An unexpected error occurred", "details": str(e)}



    
@router.get("/hii")
def hi_root(user:Session=Depends(get_current_user)):
    # Assuming `db` is the user model instance with `id` attribute
    print(f"User ID: {user.email}")
    return {"hi": "how are yiu "}


@router.get("/bye")
def by_root():  
    return {"by": "Goodby "}