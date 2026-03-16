from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    location: Optional[str] = None
    phone: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    location: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class TokenData(BaseModel):
    email: Optional[str] = None

