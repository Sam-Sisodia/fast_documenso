from pydantic import BaseModel, EmailStr,root_validator,field_serializer
from typing import Optional
from io import BytesIO
from sqlalchemy import Column, Integer, String,LargeBinary,DateTime
from apps.users.app_enum import DocumentStatus
from apps.users.app_enum import RecipientRole
from typing import List
from datetime import datetime
from apps.users.models import FieldType
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends,status,UploadFile,File
from core.database import get_db
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
    id: Optional[int] = None
    name: str
    # signature: Optional[str] = None
    # positionX: Optional[str] = None
    # positionY: Optional[str] = None
    # width: Optional[str] = None
    # height: Optional[str] = None

    class Config:
        from_attributes = True  


class RecipientSchema(BaseModel):
    id: int
    name: str
    email: str
    role: RecipientRole
    status: DocumentStatus
    signed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True




class ActiveField(BaseModel):
    id: Optional[int] = None
    signature: Optional[str] = None
    positionX: Optional[str] = None
    positionY: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    inserted: Optional[bool] = False
    field_id: int

class UserDocument(BaseModel):
    id: Optional[int] = None  # Optional, default to None
    title: Optional[str] = None
    userId: Optional[int] = None
    createdAt: Optional[datetime] = None
    file_data: Optional[str] = None
    updatedAt: Optional[datetime] = None
    status: DocumentStatus = DocumentStatus.DRAFT
    recipients: List[RecipientSchema] = []
    doc_fields: List[FieldsType] = []
    active_fields: List[ActiveField]= []

    class Config:
        from_attributes = True
    # @property
    # def custom_doc_fields(self) -> str:
    #     # from apps.users.view import ss
    #     print("++++++++++++++++++++++++++++++++",ss(d))
       
       
    #     return 

    # @field_serializer("doc_fields")
    # def serialize_custom_doc_fields(self, value) -> str:
    #     return self.custom_doc_fields




# Request schema
class Recipient(BaseModel):
    name: str
    email: EmailStr
    role: RecipientRole
    # order: int

class DocumentRecipientsRequest(BaseModel):
    document_id: int
    # fields: List[int]
    recipients: List[Recipient]



#Add fields schema
class DocumentFields(BaseModel):
    id: Optional[int] = None
    signature: Optional[str] = None
    positionX: Optional[str] = None
    positionY: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    inserted: Optional[bool] = False
    field_id: int

    class Config:
        from_attributes = True

class AddDocumentFields(BaseModel):
    document_id: int
    fields: List[DocumentFields]

    class Config:
        from_attributes = True



#Send document 

# class DocumentRecipient(BaseModel):
#     id: int


class SendDocuments(BaseModel):
    document_id: int
    # recipient: List[DocumentRecipient]
    recipient: List[int]
    subject : Optional[str] = None
    message : Optional[str] = None

    class Config:
        from_attributes = True