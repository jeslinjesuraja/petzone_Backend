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
