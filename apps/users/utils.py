# apps/users/utils.py

from passlib.context import CryptContext

# Initialize the CryptContext with bcrypt as the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from fastapi import APIRouter, HTTPException, Depends,status
from fastapi.security import OAuth2PasswordBearer

import jwt
from datetime import datetime, timedelta
from apps.users.models import User
from sqlalchemy.orm import Session
from core.database import get_db

# Secret key for signing JWT tokens (replace with a secure key in production)
SECRET_KEY = "8e0oiwuoijkjdhiu3yeihdh832yee23ue"
ALGORITHM = "HS256"  # Algorithm to use for encoding/decoding tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 120

def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # Hash the plain password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # Verify the password





def create_access_token(data: dict) -> str:
    """Generate a JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




def create_refresh_token(data: dict) -> str:
    """Generate a refresh token with a longer expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Example: 7 days expiration
    to_encode.update({"exp": expire})
    refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token


def decode_access_token(token: str) -> dict:
    """Decode a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token and extract the email
        payload = decode_access_token(token)
        email = payload.get("sub")  # Assuming "sub" is the email in the payload
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Query the user based on the email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
