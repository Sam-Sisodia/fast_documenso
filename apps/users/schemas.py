from pydantic import BaseModel, EmailStr,root_validator,field_serializer
from typing import Optional
from io import BytesIO
from sqlalchemy import Column, Integer, String,LargeBinary,DateTime
from apps.users.app_enum import DocumentStatus
from apps.users.app_enum import RecipientRole
from typing import List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    signature: Optional[str] = None 


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email :EmailStr
    password: str



   

class UserDocuments(BaseModel):
    id: int
    title: str
    userId:int
    createdAt:datetime
    updatedAt :datetime
    status: DocumentStatus = DocumentStatus.DRAFT
    class Config:
        from_attributes = True  



class GetRecipients(BaseModel):
    id: Optional[int] = None
    name :Optional[str] = None
    email : Optional[str] = None
    role : Optional[str] = None
     

    class Config:
        from_attributes = True  
    



class FieldsType(BaseModel):
    id: Optional[int] = None
    name: str
   

    class Config:
        from_attributes = True  


##########################################################################

# # typefileds :List[Fileinfo] =None

class Fileinfo(BaseModel):
    id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True  




class ActiveField(BaseModel):
    id: Optional[int] = None
    signature: Optional[str] = None
    positionX: Optional[str] = None
    positionY: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    field_id: int
   
    

    class Config:
        from_attributes = True


class RecipientSchema(BaseModel):
    id: int
    name: str
    email: str
    role: str  
    signed_at: Optional[datetime] = None
    created_at: datetime
    recipient_fields :List[ActiveField] =None
    

    class Config:
        from_attributes = True


class UserDocument(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    userId: Optional[int] = None
    createdAt: Optional[datetime] = None
    file_data: Optional[str] = None
    updatedAt: Optional[datetime] = None
    recipients: List[RecipientSchema] = []
  


    class Config:
        from_attributes = True


#########################################################################################################################

# Request schema
class Recipient(BaseModel):
    name: str
    email: EmailStr
    role: RecipientRole
    # order: int

class AssignDocumnetRecipient(BaseModel):
    document_id: int
    recipients: List[Recipient]



#Add fields schema
class DocumentFields(BaseModel):
    id: Optional[int] = None
    signature: Optional[str] = None
    positionX: Optional[str] = None
    positionY: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    page_no : Optional[str]=None
    recipient :int
    field_id: int

    class Config:
        from_attributes = True

class AddDocumentFields(BaseModel):
    document_id: int
    fields: List[DocumentFields]

    class Config:
        from_attributes = True


#Remove Documnet Fields
class RemoveDocumentFields(BaseModel):
    document_id: int
    field_ids: List[int]  # List of field IDs to delete

    class Config:
        from_attributes = True



#Send document 



class SendDocuments(BaseModel):
    document_id: int

    recipient: List[int]
    subject : Optional[str] = None
    message : Optional[str] = None

    class Config:
        from_attributes = True