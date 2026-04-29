"""
Address Model

Defines the Address document for MongoDB:
- Stores customer address details
- Linked to Customer using customer_id reference

Used for managing customer addresses.
"""
from bson import ObjectId

def create_address_doc(data: dict, address_id: str = None) -> dict:
    """Create an address document for MongoDB insertion."""
    doc = {
        "customer_id": data.get("customer_id"),
        "city": data.get("city"),
        "state": data.get("state"),
        "pincode": data.get("pincode"),
    }
    if address_id:
        doc["_id"] = ObjectId(address_id) if isinstance(address_id, str) else address_id
    return doc

def address_to_response(doc: dict) -> dict:
    """Convert MongoDB address document to API response format."""
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")) if doc.get("_id") else None,
        "customer_id": doc.get("customer_id"),
        "city": doc.get("city"),
        "state": doc.get("state"),
        "pincode": doc.get("pincode"),
    }