from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from dependencies import get_db, get_current_user
from models.pets import Pet
from models.users import User
from utils.storage import upload_image
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/pets", tags=["Pets"])
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


#  Helper to convert image paths
def normalize_pet_images(pet):
    if pet.image:
        images = pet.image if isinstance(pet.image, list) else [pet.image]
        pet.image = [
            img if img.startswith("http") or img.startswith("data:")
            else f"{BASE_URL}/{img.lstrip('/')}"
            for img in images if img
        ]
    else:
        pet.image = []
    return pet


#  Upload Image
@router.post("/upload-image")
async def upload_image_endpoint(file: UploadFile = File(...)):
    path = await upload_image(file)
    return {"url": path if path.startswith("http") else f"{BASE_URL}{path}"}


#  Get all pets
@router.get("/")
def all_pets(db: Session = Depends(get_db)):
    pets = db.query(Pet).order_by(Pet.id.desc()).all()
    return [normalize_pet_images(p) for p in pets]


#  Get my pets
@router.get("/my-pets")
def my_pets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pets = db.query(Pet).filter(Pet.owner_id == current_user.id).order_by(Pet.id.desc()).all()
    return [normalize_pet_images(p) for p in pets]


#  Get single pet
@router.get("/{pet_id}")
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    seller = db.query(User).filter(User.id == pet.owner_id).first()
    pet = normalize_pet_images(pet)

    return {
        "id": pet.id,
        "pet_name": pet.pet_name,
        "age_months": pet.age_months,
        "gender": pet.gender,
        "breed": pet.breed,
        "vaccinated": pet.vaccinated,
        "description": pet.description,
        "price": pet.price,
        "image": pet.image,
        "owner_id": pet.owner_id,
        "seller_phone": seller.phone if seller else None
    }


#  Add pet
@router.post("/sell")
async def add_pet(
    name: str = Form(...),
    type: str = Form(...),
    age: int = Form(...),
    vaccinated: str = Form(...),
    gender: str = Form(...),
    breed: str = Form(...),
    price: int = Form(...),
    description: str = Form(...),
    image_urls: List[str] = Form([]),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_vaccinated = vaccinated.lower() == "yes"

    final_images = []

    # Upload files
    for img in images:
        if img.filename:
            final_images.append(await upload_image(img))

    # Add URLs
    for url in image_urls:
        if url:
            final_images.append(url.strip())

    new_pet = Pet(
        pet_name=name,
        pet_type=type,
        breed=breed,
        age_months=age,
        gender=gender,
        vaccinated=is_vaccinated,
        description=description,
        price=price,
        image=final_images,
        owner_id=current_user.id
    )

    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)

    return {"message": "Pet posted successfully", "pet_id": new_pet.id}


#  Delete pet
@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found or not owner")

    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}


#  Update pet
@router.put("/{pet_id}")
async def update_pet(pet_id: int, pet_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found or not owner")

    for field in ["pet_name", "pet_type", "breed", "gender", "description"]:
        if field in pet_data:
            setattr(pet, field, pet_data[field])

    if "age_months" in pet_data:
        pet.age_months = int(pet_data["age_months"])

    if "price" in pet_data:
        pet.price = int(pet_data["price"])

    if "vaccinated" in pet_data:
        val = pet_data["vaccinated"]
        pet.vaccinated = val.lower() == "yes" if isinstance(val, str) else bool(val)

    if "image" in pet_data and isinstance(pet_data["image"], list):
        pet.image = [img for img in pet_data["image"] if img]

    db.commit()
    return {"message": "Pet updated successfully"}