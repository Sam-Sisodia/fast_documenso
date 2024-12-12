from sqlalchemy import Column, Integer, String,LargeBinary,DateTime,Boolean,Table
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

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    userId = Column(Integer, ForeignKey('users.id'), nullable=True)  # Foreign key to User model
    file_data = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    is_send = Column(Boolean, default=False)
    
    user = relationship('User', back_populates='documents')
    recipients = relationship(
        'Recipient',
        secondary="document_recipient",  # Use the association table directly
        back_populates='documents'
    )
    documentsharedlinks = relationship("DocumentSharedLink", back_populates="document")
    documnet_fields = relationship("CheckFields", back_populates="check_fields_document")

class Recipient(Base):
    __tablename__ = 'recipients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(RecipientRole), nullable=False)  # Role of the recipient
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.DRAFT)  # Signing status
    signed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship(
        'Document',
        secondary="document_recipient",  # Use the association table directly
        back_populates='recipients'
    )
    shared_link_recipient = relationship("DocumentSharedLink", back_populates='recipient')

class DocumentSharedLink(Base):
    __tablename__ = 'documentsharedlinks'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete="CASCADE"), nullable=False)
    recipient_id = Column(Integer, ForeignKey('recipients.id', ondelete="CASCADE"), nullable=True)  # ForeignKey to recipients

    document = relationship("Document", back_populates="documentsharedlinks")
    recipient = relationship("Recipient", back_populates="shared_link_recipient")
    created_at = Column(DateTime, default=datetime.utcnow)
    link = Column(String, nullable=False)

# Define the association table AFTER both classes are defined
document_recipient_association = Table(
    'document_recipient',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id', ondelete="CASCADE"), primary_key=True),
    Column('recipient_id', Integer, ForeignKey('recipients.id', ondelete="CASCADE"), primary_key=True)
)





class FieldType(Base):
    __tablename__ = 'fieldtype'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,unique=True, index=True)
   
    typefileds =relationship("CheckFields", back_populates="checktypefields")
    

class CheckFields(Base):
    __tablename__ = 'documnet_field'
    id = Column(Integer, primary_key=True, index=True)
    signature = Column(String, nullable=True) 
    positionX = Column(String, nullable=True) 
    positionY =Column(String, nullable=True) 
    width = Column(String, nullable=True) 
    height = Column(String, nullable=True) 
    inserted = Column(Boolean, default=False)
    document_id = Column(Integer, ForeignKey('documents.id', ondelete="CASCADE"), nullable=False) 
    field_id  = Column(Integer, ForeignKey('fieldtype.id', ondelete="CASCADE"),nullable=False)

    check_fields_document = relationship("Document", back_populates="documnet_fields")
    checktypefields =relationship("FieldType", back_populates="typefileds")

