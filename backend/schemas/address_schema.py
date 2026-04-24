"""
Address Schema

Defines data models for address operations:
- AddressCreate → input for adding address
- AddressResponse → response format for address details

Used to manage customer address data.
"""
from pydantic import BaseModel, ConfigDict, Field

class AddressBase(BaseModel):
    city: str = Field(..., description="The city of the address", example="New York")
    state: str = Field(..., description="The state or province", example="NY")
    pincode: str = Field(..., description="The postal or zip code", example="10001")

class AddressCreate(AddressBase):
    customer_id: int = Field(..., description="The ID of the customer this address belongs to", example=1)

class AddressResponse(AddressBase):
    id: int = Field(..., description="The unique identifier for the address", example=1)
    customer_id: int = Field(..., description="The ID of the customer this address belongs to", example=1)

    model_config = ConfigDict(from_attributes=True)