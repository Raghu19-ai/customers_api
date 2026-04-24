"""
User Schema

Defines data models for authentication:
- UserCreate → user registration input
- UserLogin → login credentials
- UserResponse → response after registration
- LoginResponse → JWT token response

Ensures validation and structured data for authentication APIs.
"""
from pydantic import BaseModel, EmailStr, Field


# REQUEST SCHEMAS


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address", example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, description="The unique username", example="johndoe")
    password: str = Field(..., min_length=8, description="The user's password (min 8 characters)", example="SecurePass123!")
    role: str = Field(..., description="The user's role (e.g., admin, user, superadmin)", example="admin")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "abc@gmail.com",
                "username": "abc",
                "password": "Abc@12345",
                "role": "admin"
            }
        }


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "abc@gmail.com",
                "password": "Abc@12345"
            }
        }


# RESPONSE SCHEMAS

class UserResponse(BaseModel):
    message: str
    email: str
    username: str
    role: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message": "User registered successfully",
                "email": "abc@gmail.com",
                "username": "abc",
                "role": "admin"
            }
        }


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "role": "admin"
            }
        }