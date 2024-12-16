
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
from apps.users.app_enum import DocumentStatus

def ss(db: Session):
    nn = db.query(FieldType).all()  # Query FieldType table
    return nn



@router.post("/register",response_model=schemas.UserResponse)
def register_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return JSONResponse(
            content={"msg": "Email already registered", "user": existing_user.email}, 
            status_code=400
        )
  
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
   
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
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
        file: UploadFile = File(...),  
        userId: int = Depends(get_current_user),  
        db: Session = Depends(get_db),  
    ):

        
        if file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

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
        id: int,  
        userId: int = Depends(get_current_user),  
        db: Session = Depends(get_db)  
    ):
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id  
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")
        document_data = schemas.UserDocument.from_orm(document)
    
        document_data.doc_fields = db.query(FieldType).all()  
        # document_data.active_fields = db.query(CheckFields).filter(CheckFields.document_id == id, CheckFields.inserted == True).all()
        recipients = db.query(models.Recipient).join(
            models.document_recipient_association,  # Join with the association table
            models.Recipient.id == models.document_recipient_association.c.recipient_id  # Specify the condition for joining
        ).filter(
            models.document_recipient_association.c.document_id == id  # Filter based on the document_id
        ).all()
        
        document_data.recipients = [schemas.RecipientSchema.from_orm(recipient) for recipient in recipients]

        active_fields = db.query(CheckFields).filter(
        CheckFields.document_id == id,
        ).all()

        # Add active fields to the response
        document_data.active_fields = [schemas.DocumentFields.from_orm(field) for field in active_fields]

        return document_data



    
    @router.patch("/update-document/{id}", response_model=schemas.UserDocument)
    async def update_document(
        id: int,
        document_update: schemas.UserDocument,
        userId: int = Depends(get_current_user), 
        db: Session = Depends(get_db), 
       
    ):
        # Fetch the document to update
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")

        document.title = document_update.title
        
        db.commit() 
        db.refresh(document) 

        return document  
    

    # 
    @router.delete("/delete-document/{id}")
    async def delete_document(
        id: int,  # Path parameter for document ID
        userId: int = Depends(get_current_user),  # Get the current user from OAuth or another method
        db: Session = Depends(get_db)  # Database session dependency
    ):
        # Query the document
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id
        ).first()

        # If the document does not exist, raise an error
        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")

        try:
            # Delete the document through the ORM
            db.delete(document)
            db.commit()  # Commit the transaction to trigger cascading deletes

            return {"message": "Document and associated data deleted successfully"}

        except Exception as e:
            db.rollback()  # Rollback in case of errors
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")


        



class FieldTypeManager:
    @router.post("/add-fields", response_model=schemas.FieldsType)
    async def add_fields(request: schemas.FieldsType, userId: int = Depends(get_current_user), db: Session = Depends(get_db)):
        existing_field = db.query(FieldType).filter(FieldType.name == request.name).first()
        if existing_field:
            raise HTTPException(
                status_code=400,
                detail=f"Field with name '{request.name}' already registered"
            )
        field = FieldType(
            name=request.name,
           
        )
        db.add(field)
        db.commit()
        db.refresh(field)
        return field
       
    @router.get("/get-fields")
    async def add_fields(userId: int = Depends(get_current_user),db: Session = Depends(get_db)):
        data = db.query(FieldType).all()
        return data
        
        



class RecipientManager:
    @router.get("/get-recipients/", response_model=List[schemas.GetRecipients])
    async def get_recipients(
        userId: int = Depends(get_current_user),  # Get the current user from OAuth token or other method
        db: Session = Depends(get_db)):
        recipient = db.query(models.Recipient).all()
        # return documents
        return recipient
    

    @router.post("/assign-recipients")
    async def add_recipients(
        request: schemas.DocumentRecipientsRequest,
        userId: int = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        try:
            # Fetch the document
            document = db.query(Document).filter(Document.id == request.document_id).first()
            if not document:
                return {"error": "Document not found"}

            recipients = []
            for recipient_data in request.recipients:
                # Check if the recipient already exists by email
                existing_recipient = db.query(models.Recipient).filter(
                    models.Recipient.email == recipient_data.email
                ).first()

                if existing_recipient:
                    # Check if the recipient is already associated with this document (in the M2M table)
                    existing_association = db.query(models.document_recipient_association).filter(
                        models.document_recipient_association.c.document_id == request.document_id,
                        models.document_recipient_association.c.recipient_id == existing_recipient.id
                    ).first()

                    if not existing_association:
                        # If the recipient is not already associated with this document, add the recipient to the document
                        document.recipients.append(existing_recipient)
                        recipients.append(existing_recipient)
                else:
                    # If the recipient doesn't exist, create a new recipient and associate it with the document
                    recipient = models.Recipient(
                        name=recipient_data.name,
                        email=recipient_data.email,
                        role=recipient_data.role,
                    )
                    document.recipients.append(recipient)
                    recipients.append(recipient)

            if recipients:
                db.add_all(recipients)  # Add new recipients to the session
                db.commit()  # Commit the changes to the database
                return {"message": "Recipients added successfully"}

        except Exception as e:
            db.rollback()
            return {"error": "An error occurred while adding recipients", "details": str(e)}

        
    @router.delete("/remove-recipient", status_code=204)
    async def remove_recipient_from_document(
        document_id: int,
        recipient_id: int,
        db: Session = Depends(get_db),
        userId: int = Depends(get_current_user),
    ):
        # Fetch the document from the database
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        recipient = db.query(models.Recipient).filter(models.Recipient.id == recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")

     
        if recipient in document.recipients:
            document.recipients.remove(recipient)
            db.commit()
            return {"message": "Recipient removed from the document",
                    "status":status.HTTP_200_OK }

        raise HTTPException(status_code=404, detail="Recipient not found in the document")




    @router.post("/add-document-fields")
    async def add_document_fields(request: schemas.AddDocumentFields,
            userId: int = Depends(get_current_user),
            db: Session = Depends(get_db),):
            
        try:
            # Verify the document exists
            document = db.query(Document).filter(Document.id == request.document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            fields = []
            for field_data in request.fields:
                # Check if the field already exists for the document
                existing_field = db.query(CheckFields).filter(
                    CheckFields.document_id == request.document_id,
                    CheckFields.field_id == field_data.field_id
                ).first()

                if not existing_field:
                    # Create a new CheckFields instance
                    field = CheckFields(
                        document_id=request.document_id,
                        signature=field_data.signature,
                        positionX=field_data.positionX,
                        positionY=field_data.positionY,
                        width=field_data.width,
                        height=field_data.height,
                        # inserted=field_data.inserted,
                        field_id=field_data.field_id
                    )
                    fields.append(field)

            # Add new fields to the database if any
            if fields:
                db.add_all(fields)
                db.commit()
                return {"message": "Document fields added successfully"}
            else:
                return {"message": "No new fields were added"}

        except IntegrityError as e:
            db.rollback()
            return {"error": "Database integrity error", "details": str(e)}
    

    @router.post("/remove-document-field")
    async def remove_document_field(  request: schemas.RemoveDocumentFields,
        userId: int = Depends(get_current_user),
        db: Session = Depends(get_db)):

        document = db.query(models.Document).filter(models.Document.id==request.document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found or not owned by the user")

        # Delete all fields associated with the provided field IDs
        fields_to_delete = db.query(models.CheckFields).filter(
            models.CheckFields.document_id == request.document_id,
            models.CheckFields.id.in_(request.field_ids)  # Delete specific field IDs
        )
        if not fields_to_delete.count():
            raise HTTPException(status_code=404, detail="No fields found to delete")

        # Perform the deletion
        fields_to_delete.delete(synchronize_session=False)
        db.commit()

        return {"detail": "Fields successfully deleted"}

       
                




        


    @router.post("/send-documents")
    async def send_documents(request: schemas.SendDocuments,
            userId: int = Depends(get_current_user),
            db: Session = Depends(get_db)):
            
        try:
            # Verify the document exists
            document = db.query(Document).filter(Document.id == request.document_id).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")

            document_links = []
            for data in request.recipient:
                # Check if the field already exists for the document
                existing_recipient = db.query(Recipient).filter(
                    Recipient.id == data,

                ).first()

                if  existing_recipient:
                    # Create a new CheckFields instance
                    shared_link = DocumentSharedLink(
                       token=str(uuid.uuid4()),
                        document_id=request.document_id,
                        recipient_id=existing_recipient.id,
                    )
                    document_links.append(shared_link)
            # Add new fields to the database if any
            if document_links :
                db.add_all(document_links )
                db.commit()
                recipientsmail(document_links,request.subject,request.message)

                document.is_send = True
                document.status = DocumentStatus.PENDING
                db.commit()
                
                # return {"message": "Document Send Sucessfully  successfully"}
                return {
                "message": "Document sent successfully",
                "status": status.HTTP_200_OK }
            else:
                return {"message": "No new fields were added"}

        except IntegrityError as e:
            db.rollback()
            return {"error": "Database integrity error", "details": str(e)}


          
            



    
@router.get("/hii")
def hi_root(user:Session=Depends(get_current_user)):
    # Assuming `db` is the user model instance with `id` attribute
    print(f"User ID: {user.email}")
    return {"hi": "how are yiu "}


@router.get("/bye")
def by_root():  
    return {"by": "Goodby "}