from pydantic import BaseModel, EmailStr
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




class FieldsType(BaseModel):
    id: Optional[int] = None  # Optional, default to None
    name: Optional[str] = None


class UserDocument(BaseModel):
    id: Optional[int] = None  # Optional, default to None
    title: Optional[str] = None
    userId: Optional[int] = None
    createdAt: Optional[datetime] = None
    file_data: Optional[str] = None
    updatedAt: Optional[datetime] = None
    status: DocumentStatus = DocumentStatus.DRAFT
    

    class Config:
        from_attributes = True



#Recipient


# Request schema
class Recipient(BaseModel):
    name: str
    email: EmailStr
    role: RecipientRole
    # order: int

class DocumentRecipientsRequest(BaseModel):
    document_id: int
    recipients: List[Recipient]
