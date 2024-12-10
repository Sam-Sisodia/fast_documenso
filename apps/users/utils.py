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
import smtplib
from email.mime.text import MIMEText
import os


# Secret key for signing JWT tokens (replace with a secure key in production)
SECRET_KEY = "8e0oiwuoijkjdhiu3yeihdh832yee23ue"
ALGORITHM = "HS256"  # Algorithm to use for encoding/decoding tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

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



# def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode the token and extract the email
#         payload = decode_access_token(token)
#         email = payload.get("sub")  # Assuming "sub" is the email in the payload
        
#         if email is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token"
#             )
        
#         # Query the user based on the email
#         user = db.query(User).filter(User.email == email).first()
        
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="User not found"
#             )
        
#         return user
    
#     except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token"
#         )

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Decode the token and extract the payload
        payload = decode_access_token(token)  
        email = payload.get("sub")  
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: email (sub) not found"
            )

        # Query the user based on the email
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user

    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"An error occurred while processing the token: {str(e)}")




def recipientsmail(document_links,subject,message):
    results = []  # List to store results for each email attempt

    for link in document_links:
        # Email details
        sender_email = "sajal@example.com"
        receiver_email = link.recipient
        subject =    subject  if subject else  "Shared Documents" 
        url = f'http://127.0.0.1:8000/api/user-document/{link.document_id}/?token={link.token}'
        user_message = message if message else ""
        body = f"{user_message} Click on link to open the Document {url}"
       
        # Set up the MIMEText object
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email.email

        # SMTP server configuration (example with Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = "sajal89304@gmail.com"
        smtp_password = os.getenv("EMAIL_PASSWORD")

        try:
            # Connect to SMTP server
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure connection
                server.login(smtp_user, smtp_password)
                print("Sending email to:", receiver_email.email)
                server.sendmail(sender_email, receiver_email.email, msg.as_string())
            results.append({"recipient": receiver_email.email, "status": "Email sent successfully"})
        except Exception as e:

            results.append({"recipient": receiver_email.email, "status": f"Failed to send email: {e}"})
   
    return results  # Return results after sending all emails

        


