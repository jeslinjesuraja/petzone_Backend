from pydantic import BaseModel
from typing import Optional

class PetBase(BaseModel):
    pet_name: str
    pet_type: str
    breed: str
    age_months: int
    gender: str
    vaccinated: str
    description: str
    price: int

class PetCreate(BaseModel):
    pet_name: str
    pet_type: str
    breed: str
    age_months: int
    gender: str
    vaccinated: str
    description: str
    price: int
    owner_id: int

# class PetCreate(BaseModel):
#     pet_name: str
#     pet_type: str
#     breed: Optional[str] = None
#     age_months: int
#     gender: Optional[str] = None
#     vaccinated: bool
#     description: Optional[str] = None
#     price: int
#     image: Optional[str] = None
#     owner_id: int

# class PetResponse(PetCreate):
#     id: int
#     class Config:
#         orm_mode = True