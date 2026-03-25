# import os
# import hashlib
# import bcrypt
# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from dotenv import load_dotenv

# load_dotenv()

# # JWT Config
# SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key-change-it-in-env")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 hours

# def _pre_hash_password(password: str) -> bytes:
#     """Pre-hashes a password with SHA256 to handle bcrypt's 72-byte limit."""
#     return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verifies a password by pre-hashing it first using direct bcrypt."""
#     try:
#         return bcrypt.checkpw(_pre_hash_password(plain_password), hashed_password.encode("utf-8"))
#     except Exception:
#         return False

# def get_password_hash(password: str) -> str:
#     """Hashes a password by pre-hashing it with SHA256 first using direct bcrypt."""
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(_pre_hash_password(password), salt)
#     return hashed.decode("utf-8")

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


import os
import hashlib
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key-change-it-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def _pre_hash_password(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_pre_hash_password(plain_password), hashed_password.encode("utf-8"))
    except:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(_pre_hash_password(password), bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {**data, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)