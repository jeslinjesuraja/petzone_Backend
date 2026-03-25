from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentCreate(BaseModel):
    pet_id: int
    amount: float
    payment_method: str
    transaction_id: str

class PaymentResponse(BaseModel):
    id: int
    pet_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
