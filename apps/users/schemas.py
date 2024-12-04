from pydantic import BaseModel, EmailStr
from typing import Optional
from io import BytesIO

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