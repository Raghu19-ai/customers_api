
"""
User Model

Defines the User table for authentication:
- Stores email, password, and role
- Used for login and authorization

Supports role-based access control.
"""
from sqlalchemy import Column, Integer, String
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String)

    # NEW FIELD AS ROLE
    role = Column(String, default="user")  