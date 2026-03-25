from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.session import Base

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    pet_name = Column(String, nullable=False)
    pet_type = Column(String, nullable=False)
    breed = Column(String)
    age_months = Column(Integer)
    gender = Column(String)
    vaccinated = Column(Boolean)
    description = Column(String)
    price = Column(Integer)
    image = Column(JSON) 
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="pets")
    messages = relationship("Message", back_populates="pet")

