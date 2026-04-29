"""
Customer Model

Defines the Customer document structure for MongoDB:
- Stores personal, contact, and professional details
- References Address documents via customer_id

Used for database operations related to customers.
"""
from datetime import datetime
from bson import ObjectId

def create_customer_doc(data: dict, customer_id: str = None) -> dict:
    """Create a customer document for MongoDB insertion."""
    now = datetime.utcnow().isoformat()
    doc = {
        "name": data.get("name"),
        "age": data.get("age"),
        "gender": data.get("gender"),
        "date_of_birth": data.get("date_of_birth"),
        "email": data.get("email", "").lower().strip() if data.get("email") else None,
        "phone": data.get("phone"),
        "alternate_phone": data.get("alternate_phone"),
        "company": data.get("company"),
        "job_title": data.get("job_title"),
        "experience_years": data.get("experience_years"),
        "customer_type": data.get("customer_type"),
        "status": data.get("status"),
        "notes": data.get("notes"),
        "source": data.get("source"),
        "created_at": data.get("created_at", now),
        "updated_at": data.get("updated_at", now),
    }
    if customer_id:
        doc["_id"] = ObjectId(customer_id) if isinstance(customer_id, str) else customer_id
    return doc

def customer_to_response(doc: dict) -> dict:
    """Convert MongoDB customer document to API response format."""
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")) if doc.get("_id") else None,
        "name": doc.get("name"),
        "age": doc.get("age"),
        "gender": doc.get("gender"),
        "date_of_birth": doc.get("date_of_birth"),
        "email": doc.get("email"),
        "phone": doc.get("phone"),
        "alternate_phone": doc.get("alternate_phone"),
        "company": doc.get("company"),
        "job_title": doc.get("job_title"),
        "experience_years": doc.get("experience_years"),
        "customer_type": doc.get("customer_type"),
        "status": doc.get("status"),
        "notes": doc.get("notes"),
        "source": doc.get("source"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }