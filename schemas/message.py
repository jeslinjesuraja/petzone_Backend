from pydantic import BaseModel, EmailStr
# from typing import Optional


class MessageCreate(BaseModel):
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: str
    message: str
    pet_id: int


