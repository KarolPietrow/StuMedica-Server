from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    # age = Column(Integer) # Opcjonalnie, jeśli używasz
    account_type = Column(String, nullable=False)  # 'patient' lub 'doctor'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    medications = relationship("Medication", back_populates="owner")

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    note = Column(String, nullable=True)
    reminders = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="medications")