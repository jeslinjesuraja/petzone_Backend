from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.session import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    location = Column(String)
    phone = Column(String)
    password = Column(String, nullable=False)
    pets = relationship("Pet", back_populates="owner")
