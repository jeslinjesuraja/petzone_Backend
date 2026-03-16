from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.session import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False) # 'card' or 'upi'
    transaction_id = Column(String, unique=True, index=True)
    status = Column(String, default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
