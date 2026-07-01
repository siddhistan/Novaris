import os
from dotenv import load_dotenv
from passlib.context import CryptContext


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This reads our .env file from the project root
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))


CLIENT_URL = os.getenv("CLIENT_URL")



#This block loads configuration values from the .env file and stores them as variables used for JWT, token expiry, and security settings
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_finsolve")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

#These variables  are stored as int and float,cuz they are stored as strings in env file, and we will need these values to do some math
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

REFRESH_TOKEN_EXPIRE_DAYS = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ABSOLUTE_SESSION_EXPIRE_DAYS = float(os.getenv("ABSOLUTE_SESSION_EXPIRE_DAYS", "30"))

MAX_FAILED_ATTEMPTS = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))  
LOCKOUT_BASE_MINUTES = float(os.getenv("LOCKOUT_BASE_MINUTES", "1"))
LOCKOUT_RESET_HOURS = float(os.getenv("LOCKOUT_RESET_HOURS", "24"))


# Use Argon2 for hashing
#It creates a password hashing manager
#"This object knows how to hash passwords and verify them using Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")