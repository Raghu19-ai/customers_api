
"""
Customer Model

Defines the Customer table structure:
- Stores personal, contact, and professional details
- Maintains relationship with Address table

Used for database operations related to customers.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Personal
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    date_of_birth = Column(String)

    # Contact
    email = Column(String)
    phone = Column(String)
    alternate_phone = Column(String)

    # Professional
    company = Column(String)
    job_title = Column(String)
    experience_years = Column(Integer)

    # System
    customer_type = Column(String)
    status = Column(String)

    # Tracking
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Extra
    notes = Column(String)
    source = Column(String)

    addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")