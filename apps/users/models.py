from sqlalchemy import Column, Integer, String
from core.database import Base  # Import Base instead of redefining it

class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
