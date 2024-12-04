from pydantic import BaseModel, EmailStr
from typing import Optional
from io import BytesIO
from sqlalchemy import Column, Integer, String,LargeBinary,DateTime
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
        orm_mode = True



class UserLogin(BaseModel):
    email :EmailStr
    password: str






class UserDocuments(BaseModel):
    id: int
    title: str
    userId:int
    file_data:str
    createdAt:datetime
    updatedAt :datetime



    class Config:
        orm_mode = True  