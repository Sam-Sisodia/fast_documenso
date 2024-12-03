from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Base here
Base = declarative_base()

def get_db():
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Yield the session to the route
    finally:
        db.close() 