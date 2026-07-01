from datetime import datetime, timedelta, timezone

from jose import jwt
from jose import JWTError, ExpiredSignatureError

from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)



# Create JWT token, called from login endpoint
def create_access_token(data: dict):       #emp_id and role is sent as parameter here
    to_encode = data.copy()             

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  #creates expiry time
    to_encode.update({"exp": int(expire.timestamp())})  # convert to UNIX timestamp, add expiry to payload of jwt

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  #encodes the jwt, signs it using secret key
    return encoded_jwt    #returns the jwt payload to main






# Verify JWT token
from jose import JWTError, ExpiredSignatureError    #These are exceptions thrown by jwt.decode(), and without catching them your program will crash.

#called from ask endpoint
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #internally the function checks signature, algorithm, expiry and the token format
        
        # Even if JWT signature is valid, it does not guarantee required fields exist.
        # "sub" represents the user identity (emp_id), so we verify its presence
        # to prevent crashes and ensure correct authentication flow  
        if "sub" not in payload or "session_start" not in payload:      
            return None
        
        return payload       #if everything is valid, jwt token string is returned to main
    
    except ExpiredSignatureError:
        print("Token expired")         #if token has expired
        return None
    
    except JWTError:
        print("Invalid token")           #if token is tampered, malformed, wrong signature
        return None
    