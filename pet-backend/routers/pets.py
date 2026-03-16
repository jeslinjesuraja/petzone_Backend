from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import time
from dependencies import get_db, get_current_user
from models.pets import Pet
from models.users import User
from utils.storage import upload_image

import os
from dotenv import load_dotenv
load_dotenv()

# Router for handling all pet-related operations
router = APIRouter(prefix="/pets", tags=["Pets"])

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

@router.post("/upload-image")
async def upload_image_endpoint(file: UploadFile = File(...)):
    """Upload a single image and return its full URL."""
    saved_path = await upload_image(file)
    if saved_path.startswith('http'):
        return {"url": saved_path}
    return {"url": f"{BASE_URL}{saved_path}"}

def normalize_pet_images(pet):
    """Convert local image paths to full URLs in pet response."""
    if pet.image:
        images = pet.image if isinstance(pet.image, list) else [pet.image]
        full_urls = []
        for img in images:
            if not img:
                continue
            img = img.strip()
            # If it's a full URL (http) or Base64, it's already normalized
            if img.startswith('http') or img.startswith('data:'):
                full_urls.append(img)
            else:
                # Local path: prepend BASE_URL
                clean_path = img.lstrip('/')
                full_urls.append(f"{BASE_URL}/{clean_path}")
        pet.image = full_urls
    else:
        pet.image = []
    return pet

@router.get("/")
def all_pets(db: Session = Depends(get_db)):
    pets = db.query(Pet).order_by(Pet.id.desc()).all()
    return [normalize_pet_images(p) for p in pets]

@router.get("/my-pets")
def my_pets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pets = db.query(Pet).filter(Pet.owner_id == current_user.id).order_by(Pet.id.desc()).all()
    return [normalize_pet_images(p) for p in pets]



@router.get("/{pet_id}")
def get_pet(pet_id: int, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Get seller details
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
@router.post("/sell")
async def add_pet(
    name: str = Form(None),
    type: str = Form(None),
    age: int = Form(None),
    vaccinated: str = Form(None),
    gender: str = Form(None),
    breed: str = Form(None),
    price: int = Form(None),
    description: str = Form(None),
    image_urls: List[str] = Form([]),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    with open("debug_add_pet.log", "a") as f:
        f.write(f"ID: {current_user.id}, image_urls: {image_urls}\n")
    print(f"DEBUG: name={name}, type={type}, age={age}, vaccinated={vaccinated}, breed={breed}, price={price}")
    print(f"DEBUG: image_urls={image_urls}, files={[f.filename for f in images]}")

    # Validate required fields
    required = {"name": name, "type": type, "age": age, "gender": gender, "breed": breed, "price": price, "description": description}
    missing = [k for k, v in required.items() if v is None or (isinstance(v, str) and not v.strip())]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    is_vaccinated = vaccinated.lower() == "yes" if vaccinated else False

    # Process all image sources (Files and URLs)
    final_image_paths = []

    # 1. Process File Uploads
    if images:
        for img in images:
            if img.filename:
                saved_path = await upload_image(img)
                final_image_paths.append(saved_path)

    # 2. Process URL/Base64 Inputs
    if image_urls:
        for url in image_urls:
            url = url.strip()
            if not url: continue

            # Skip re-uploading if it's already a Cloudinary URL or a Base64 string
            is_cloudinary = "cloudinary.com" in url
            is_base64 = url.startswith('data:')
            is_local = url.startswith(BASE_URL) or ":5000" in url or "localhost" in url or "127.0.0.1" in url
            
            if is_cloudinary or is_base64:
                final_image_paths.append(url)
            elif url.startswith('http') and not is_local:
                # Truly external URL (like a direct link to another site), download it
                try:
                    saved_path = await upload_image(url)
                    final_image_paths.append(saved_path)
                except Exception as e:
                    print(f"Failed to download external image {url}: {e}")
                    final_image_paths.append(url)
            else:
                # Local URL or relative path
                rel_path = url.split(":5000")[-1] if ":5000" in url else url.replace(BASE_URL, "")
                if rel_path not in final_image_paths:
                    final_image_paths.append(rel_path)

    new_pet = Pet(
        pet_name=name,
        pet_type=type,
        breed=breed,
        age_months=age,
        gender=gender,
        vaccinated=is_vaccinated,
        description=description,
        price=price,
        image=final_image_paths,
        owner_id=current_user.id
    )

    db.add(new_pet)
    db.commit()
    db.refresh(new_pet)

    return {"message": "Pet posted successfully", "pet_id": new_pet.id}

@router.delete("/{pet_id}")
def delete_pet(pet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found or you are not the owner")
    db.delete(pet)
    db.commit()
    return {"message": "Pet deleted successfully"}

@router.put("/{pet_id}")
async def update_pet(pet_id: int, pet_data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pet = db.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == current_user.id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found or you are not the owner")
    
    print(f"DEBUG: update_pet data received: {pet_data}")
    
    try:
        if "pet_name" in pet_data: pet.pet_name = pet_data["pet_name"]
        if "pet_type" in pet_data: pet.pet_type = pet_data["pet_type"]
        if "breed" in pet_data: pet.breed = pet_data["breed"]
        if "age_months" in pet_data: pet.age_months = int(pet_data["age_months"])
        if "gender" in pet_data: pet.gender = pet_data["gender"]
        if "vaccinated" in pet_data:
            val = pet_data["vaccinated"]
            if isinstance(val, str):
                pet.vaccinated = val.lower() == "yes"
            else:
                pet.vaccinated = bool(val)
        if "description" in pet_data: pet.description = pet_data["description"]
        if "price" in pet_data: pet.price = int(pet_data["price"])
    except (ValueError, TypeError) as e:
        print(f"DEBUG: Error converting types: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data format: {e}")
    
    # Handle image updates if provided in pet_data (as a list of URLs/paths)
    if "image" in pet_data:
        new_images = pet_data["image"]
        if isinstance(new_images, list):
            # Process URLs to download them if needed
            processed_images = []
            for img in new_images:
                if not img: continue
                # Robust self-hosted check for update
                is_self_hosted = img.startswith(BASE_URL) or \
                                 img.startswith("http://localhost:5000") or \
                                 img.startswith("http://127.0.0.1:5000")
                
                if img.startswith('data:'):
                    processed_images.append(img)
                elif is_self_hosted:
                    rel_path = img.split(":5000")[-1] if ":5000" in img else img.replace(BASE_URL, "")
                    processed_images.append(rel_path)
                elif img.startswith('http'):
                    try:
                        saved_path = await upload_image(img)
                        processed_images.append(saved_path)
                    except:
                        processed_images.append(img)
                else:
                    processed_images.append(img)
            pet.image = processed_images

    db.commit()
    return {"message": "Pet updated successfully"}