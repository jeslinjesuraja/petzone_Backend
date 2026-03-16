from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    buyer_name = Column(String, nullable=False)
    buyer_email = Column(String, nullable=False)
    buyer_phone = Column(String)
    message = Column(String)
    pet_id = Column(Integer, ForeignKey("pets.id"))
    pet = relationship("Pet", back_populates="messages")


    