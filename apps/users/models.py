from sqlalchemy import Column, Integer, String,LargeBinary,DateTime
from sqlalchemy import  Enum as SQLAlchemyEnum
from core.database import Base  # Import Base instead of redefining it
from datetime import datetime
from sqlalchemy.orm import relationship
from apps.users.app_enum import DocumentStatus,RecipientRole
from sqlalchemy import ForeignKey



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    signature = Column(String, nullable=True) 

    # documents = relationship('Document', backref='user', lazy='dynamic')
    documents = relationship('Document', back_populates='user')





class FieldType(Base):
    __tablename__ = 'FieldType'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,unique=True, index=True)



    

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    # externalId = Column(String, index=True)
    title = Column(String)
    userId = Column(Integer, ForeignKey('users.id'), nullable=True)  # Foreign key to User model
    file_data = Column(String, nullable=True) 
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.DRAFT)  # Enum field
    user = relationship('User', back_populates='documents')





# class Assign(Base):
#     __tablename__ = 'assignrsuser'

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, index=True)
#     email = Column(String, unique=True, index=True)
#     status = Column(SQLAlchemyEnum(RecipientRole), default=RecipientRole.SIGNER)



    


