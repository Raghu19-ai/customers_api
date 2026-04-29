"""
Customer Schema

Defines data models for customer operations:
- CustomerCreate → input for creating/updating customers (POST/PUT)
- CustomerUpdate → partial update schema (PATCH)
- CustomerResponse → response format including addresses

Handles validation and API documentation for customer data.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from .address_schema import AddressResponse



# CREATE SCHEMA (POST / PUT)
class CustomerCreate(BaseModel):
    name: str = Field(..., description="The full name of the customer", example="abc")
    age: int = Field(..., description="The age of the customer", example=22)
    gender: str = Field(..., description="The gender of the customer", example="Male")
    date_of_birth: str = Field(..., description="Date of birth in YYYY-MM-DD format", example="2002-01-01")

    email: str = Field(..., description="The email address of the customer", example="raghu@gmail.com")
    phone: str = Field(..., description="The primary phone number", example="9876543210")
    alternate_phone: Optional[str] = Field(None, description="An alternate phone number", example="9123456780")

    company: str = Field(None, description="The company where the customer works", example="ABC Corp")
    job_title: str = Field(None, description="The job title of the customer", example="Developer")
    experience_years: int = Field(None, description="Years of professional experience", example=2)

    customer_type: Optional[str] = Field(None, description="The type of customer (e.g., Premium, Standard)", example="Premium")
    status: Optional[str] = Field(None, description="The current status of the customer (e.g., Active, Inactive)", example="Active")

    notes: Optional[str] = Field("", description="Any additional notes about the customer", example="Important client")
    source: Optional[str] = Field("", description="The source from where the customer was acquired", example="Website")

    created_at: Optional[str] = Field(None, description="The timestamp when the customer was created")
    updated_at: Optional[str] = Field(None, description="The timestamp when the customer was last updated")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "abc",
                "age": 22,
                "gender": "Male",
                "date_of_birth": "2002-01-01",
                "email": "abc@gmail.com",
                "phone": "9876543210",
                "alternate_phone": "9123456780",
                "company": "ABC Corp",
                "job_title": "Developer",
                "experience_years": 2,
                "customer_type": "Premium",
                "status": "Active",
                "notes": "Important client",
                "source": "Website"
            }
        }



# UPDATE SCHEMA (PATCH)
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None

    company: Optional[str] = None
    job_title: Optional[str] = None
    experience_years: Optional[int] = None

    customer_type: Optional[str] = None
    status: Optional[str] = None

    notes: Optional[str] = None
    source: Optional[str] = None

    updated_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "Inactive",
                "job_title": "Senior Developer"
            }
        }



# RESPONSE SCHEMA
class CustomerResponse(CustomerCreate):
    id: str
    addresses: List[AddressResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True