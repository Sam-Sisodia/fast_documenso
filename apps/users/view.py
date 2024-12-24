
from fastapi import APIRouter

import base64
from fastapi import APIRouter, HTTPException, Depends,status,UploadFile,File,Form
from sqlalchemy.orm import Session

from apps.users import models,schemas,utils
from apps.users.models import User,Document,FieldType,Recipient,DocumentSharedLink,CheckFields,DocumentSigningProcess,DocumentStatus,document_recipient_association
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
from apps.users.app_enum import DocumentStatus,SigningOrder

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
        signing_order: SigningOrder = Form(None),
        # note: str =None,
        note: str = Form(None),
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
            signing_order = signing_order,
            note=note,
            
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
        document = db.query(models.Document).options(
            joinedload(models.Document.recipients)
        ).filter(
            models.Document.userId == userId.id,
            models.Document.id == id  
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")
        
    
        recipients_data = []
        for recipient in document.recipients:
            active_fields_data = db.query(models.CheckFields).filter(
                models.CheckFields.document_id == id,
                models.CheckFields.recipient_id == recipient.id
            ).all()

            recipient_fields = [
                schemas.ActiveField.from_orm(field) for field in active_fields_data
            ]

            recipient_data = schemas.RecipientSchema.from_orm(recipient)
            recipient_data.recipient_fields = recipient_fields

            recipients_data.append(recipient_data)
        document_data = schemas.UserDocument.from_orm(document)
        document_data.recipients = recipients_data

        return document_data

    
    @router.patch("/update-document/{id}", response_model=schemas.UserDocument)
    async def update_document(
        id: int,
        document_update: schemas.UserDocument,
        userId: int = Depends(get_current_user), 
        db: Session = Depends(get_db), 
       
    ):
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
        id: int,  
        userId: int = Depends(get_current_user),  
        db: Session = Depends(get_db)  
    ):
        # Query the document
        document = db.query(models.Document).filter(
            models.Document.userId == userId.id,
            models.Document.id == id
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found for the user")

        try:
            db.delete(document)
            db.commit()  

            return {"message": "Document and associated data deleted successfully"}

        except Exception as e:
            db.rollback()  
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
        request: schemas.AssignDocumnetRecipient,
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
    async def add_document_fields(
        request: schemas.AddDocumentFields,
        userId: int = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        try:
            # Verify the document exists
            document = db.query(Document).filter(Document.id == request.document_id).first()
           
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            exists_query = db.query(document_recipient_association).filter(
                        document_recipient_association.c.document_id == request.document_id
                    ).first()
            
            if not exists_query:
                raise HTTPException(status_code=404, detail="No document assign yet")



            fields = []

            for field_data in request.fields:
                recipient = db.query(Recipient).filter(Recipient.id == field_data.recipient).first()
            
                if not recipient:
                    raise HTTPException(status_code=404, detail="Recipient not found")
                
                # Check if the field already exists for this document and recipient
                existing_field = db.query(CheckFields).filter(
                    CheckFields.document_id == request.document_id,
                    CheckFields.recipient_id == field_data.recipient,
                    CheckFields.field_id == field_data.field_id,
                    CheckFields.positionX == field_data.positionX,
                    CheckFields.positionY == field_data.positionY,
                ).first()

                if not existing_field:
                    # Create a new CheckFields instance
                    field = CheckFields(
                        document_id=request.document_id,
                        recipient_id=field_data.recipient,
                        signature=field_data.signature,
                        positionX=field_data.positionX,
                        positionY=field_data.positionY,
                        width=field_data.width,
                        height=field_data.height,
                        page_no=field_data.page_no,
                        field_id=field_data.field_id,
                    )
                    fields.append(field)

            # Add new fields to the database
            if fields:
                db.add_all(fields)
                db.commit()
                return {"message": "Document fields added successfully"}
            else:
                return {"message": "No new fields were added. Fields already exist."}

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


          
          
    @router.get("/get-sign-document/{recipient_token}",response_model=schemas.GetSignDocument)
    async def get_recipient_document(
        recipient_token: str,
        db: Session = Depends(get_db),
        userId: int = Depends(get_current_user)):
        sign_recipient = db.query(DocumentSharedLink).filter(DocumentSharedLink.token == recipient_token).first()
      
        
        if not sign_recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        document = db.query(models.Document).filter(models.Document.id == sign_recipient.document_id).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

      
        recipient_data = None
        for recipient in document.recipients:
            if recipient.id == sign_recipient.recipient_id:  # Matching recipient
                active_fields_data = db.query(models.CheckFields).filter(
                    models.CheckFields.document_id == document.id,
                    models.CheckFields.recipient_id == recipient.id
                ).all()

                recipient_fields = [
                    schemas.ActiveField.from_orm(field) for field in active_fields_data
                ]

                recipient_data = schemas.RecipientSchema.from_orm(recipient)
                recipient_data.recipient_fields = recipient_fields
                break  
        if recipient_data:
            document_data = schemas.UserDocument.from_orm(document)
            document_data.recipients = [recipient_data]
            return document_data
        else:
            raise HTTPException(status_code=404, detail="Recipient data not found")
     
    @router.post("/sign-document/{recipient_token}")
    async def sign_document(
        request: schemas.SignDocuments,  # Request schema for signing documents
        db: Session = Depends(get_db),  # Dependency for getting the database session
        userId: int = Depends(get_current_user)  # Dependency for getting the current user ID
    ):
        # Fetch recipient by the provided token from the URL path
        recipient = db.query(DocumentSharedLink).filter(DocumentSharedLink.token == request.token).first()

        # If no recipient is found, raise a 404 error
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")

        # Get the current UTC time when the recipient is signing the document
        current_time = datetime.utcnow()
        document_type = db.query(Document).filter(Document.id == recipient.document_id).first()

        # Check if the document signing order is SEQUENTIAL
        if document_type.signing_order == SigningOrder.SEQUENTIAL:
        
            # Fetch all recipients for this document in the correct signing order
            recipients_in_order = db.query(CheckFields).filter(
                CheckFields.document_id == recipient.document_id,  # Ensure it belongs to the same document
                CheckFields.recipient_id.isnot(None)  # Make sure to only include recipients
            ).order_by(CheckFields.order.asc()).all()  # Order by the 'order' field (the signing order)

            # If no recipients are found for this document, raise a 404 error
            if not recipients_in_order:
                raise HTTPException(status_code=404, detail="No recipients found for this document")

            # Extract the list of recipient IDs in signing order
            recipient_orders = [field.recipient_id for field in recipients_in_order]

            # Ensure that the current recipient is part of the signing order
            if recipient.recipient_id not in recipient_orders:
                raise HTTPException(status_code=404, detail="Recipient not found in signing order")

            # Check the position of the current recipient in the signing order
            recipient_position = recipient_orders.index(recipient.recipient_id)

            # If the recipient is not the first one, check if the previous recipient has signed
            if recipient_position > 0:
                # Get the previous recipient's ID in the order
                previous_recipient_id = recipient_orders[recipient_position - 1]

                # Query the previous recipient from the Recipient table
                previous_recipient = db.query(Recipient).filter(Recipient.id == previous_recipient_id).first()

                # Fetch the 'CheckFields' record for the previous recipient to check if they signed
                previous_field = db.query(CheckFields).filter(
                    CheckFields.document_id == recipient.document_id,
                    CheckFields.recipient_id == previous_recipient_id
                ).first()

                # If the previous recipient hasn't signed, raise an error
                if not previous_field or not previous_field.inserted:
                    raise HTTPException(status_code=400, detail=f"Recipient {previous_recipient.email} must sign first")

        # Fetch the current recipient's signing field from the 'CheckFields' table
        current_field = db.query(CheckFields).filter(
            CheckFields.document_id == recipient.document_id,
            CheckFields.recipient_id == recipient.recipient_id
        ).first()

        # If no signing field is found for the current recipient, raise a 404 error
        if not current_field:
            raise HTTPException(status_code=404, detail="Recipient's sign field not found")

        # If the current recipient has already signed, raise a 400 error
        if current_field.inserted:
            raise HTTPException(status_code=400, detail="Recipient already signed the document")

        # Mark the current recipient's field as signed by updating the 'inserted' field and setting the sign time
        current_field.inserted = True
        current_field.signed_at = current_time

        # Commit the changes to the database
        db.commit()

        # Return a success message with the recipient's email and their sign position (1-indexed for clarity)
        return {
            "message": "Document signed successfully",
            "recipient": recipient.recipient.email,  # Returning the recipient's email who signed
            # "sign_position": recipient_position + 1  # Returning the recipient's signing position (1-indexed)
        }


    # @router.post("/sign-document/{recipient_token}")
    # async def sign_document(
    #     request: schemas.SignDocuments,  # Request schema for signing documents
    #     db: Session = Depends(get_db),  # Dependency for getting the database session
    #     userId: int = Depends(get_current_user)  # Dependency for getting the current user ID
    # ):
    #     # Fetch recipient by the provided token from the URL path
    #     recipient = db.query(DocumentSharedLink).filter(DocumentSharedLink.token == request.token).first()
        
    #     # If no recipient is found, raise a 404 error
    #     if not recipient:
    #         raise HTTPException(status_code=404, detail="Recipient not found")
        
    #     # Get the current UTC time when the recipient is signing the document
    #     current_time = datetime.utcnow()
    #     document_type = db.query(Document).filter(Document.id ==recipient.document_id).first()
    #     print(document_type.signing_order.value)
        
    #     if document_type.signing_order == document_type.signing_order..value:
    #         print("+++++++++")
            
        
        
        
        

    #     # Fetch all recipients for this document in the correct signing order
    #     recipients_in_order = db.query(CheckFields).filter(
    #         CheckFields.document_id == recipient.document_id,  # Ensure it belongs to the same document
    #         CheckFields.recipient_id.isnot(None)  # Make sure to only include recipients
    #     ).order_by(CheckFields.order.asc()).all()  # Order by the 'order' field (the signing order)

    #     # If no recipients are found for this document, raise a 404 error
    #     if not recipients_in_order:
    #         raise HTTPException(status_code=404, detail="No recipients found for this document")

    #     # Extract the list of recipient IDs in signing order
    #     recipient_orders = [field.recipient_id for field in recipients_in_order]
        
    #     # Ensure that the current recipient is part of the signing order
    #     if recipient.recipient_id not in recipient_orders:
    #         raise HTTPException(status_code=404, detail="Recipient not found in signing order")

    #     # Check the position of the current recipient in the signing order
    #     recipient_position = recipient_orders.index(recipient.recipient_id)
        
    #     # If the recipient is not the first one, check if the previous recipient has signed
    #     if recipient_position > 0:
    #         # Get the previous recipient's ID in the order
    #         previous_recipient_id = recipient_orders[recipient_position - 1]
            
    #         # Query the previous recipient from the Recipient table
    #         previous_recipient = db.query(Recipient).filter(Recipient.id == previous_recipient_id).first()

    #         # Fetch the 'CheckFields' record for the previous recipient to check if they signed
    #         previous_field = db.query(CheckFields).filter(
    #             CheckFields.document_id == recipient.document_id,
    #             CheckFields.recipient_id == previous_recipient_id
    #         ).first()

    #         # If the previous recipient hasn't signed, raise an error
    #         if not previous_field or not previous_field.inserted:
    #             raise HTTPException(status_code=400, detail=f"Recipient {previous_recipient.email} must sign first")

    #     # Fetch the current recipient's signing field from the 'CheckFields' table
    #     current_field = db.query(CheckFields).filter(
    #         CheckFields.document_id == recipient.document_id,
    #         CheckFields.recipient_id == recipient.recipient_id
    #     ).first()

    #     # If no signing field is found for the current recipient, raise a 404 error
    #     if not current_field:
    #         raise HTTPException(status_code=404, detail="Recipient's sign field not found")

    #     # If the current recipient has already signed, raise a 400 error
    #     if current_field.inserted:
    #         raise HTTPException(status_code=400, detail="Recipient already signed the document")

    #     # Mark the current recipient's field as signed by updating the 'inserted' field and setting the sign time
    #     current_field.inserted = True
    #     current_field.signed_at = current_time

    #     # Commit the changes to the database
    #     db.commit()

    #     # Return a success message with the recipient's email and their sign position (1-indexed for clarity)
    #     return {
    #         "message": "Document signed successfully",
    #         "recipient": recipient.recipient.email,  # Returning the recipient's email who signed
    #         "sign_position": recipient_position + 1  # Returning the recipient's signing position (1-indexed)
    #     }

            

            

   