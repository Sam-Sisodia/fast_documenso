from sqlalchemy import Column, Integer, String,LargeBinary
from core.database import Base  # Import Base instead of redefining it



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    signature = Column(LargeBinary, nullable=True) 