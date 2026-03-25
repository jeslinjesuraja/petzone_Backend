from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
from models.message import Message
from models.pets import Pet
from schemas.message import MessageCreate

router = APIRouter(prefix="/messages")





@router.post("/")
def send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    if not db.query(Pet).filter(Pet.id == msg.pet_id).first():
        raise HTTPException(status_code=404, detail="Pet not found")

    new_msg = Message(**msg.dict())
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@router.get("/pet/{pet_id}")
def pet_inquiries(pet_id: int, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.pet_id == pet_id).all()
