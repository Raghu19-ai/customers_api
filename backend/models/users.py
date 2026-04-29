"""
User Model

Defines the User document for MongoDB authentication:
- Stores email, password, and role
- Used for login and authorization

Supports role-based access control.
"""
from bson import ObjectId

def create_user_doc(data: dict, user_id: str = None) -> dict:
    """Create a user document for MongoDB insertion."""
    doc = {
        "email": data.get("email", "").lower().strip() if data.get("email") else None,
        "username": data.get("username", "").lower().strip() if data.get("username") else None,
        "password": data.get("password"),
        "role": data.get("role", "user"),
    }
    if user_id:
        doc["_id"] = ObjectId(user_id) if isinstance(user_id, str) else user_id
    return doc

def user_to_response(doc: dict) -> dict:
    """Convert MongoDB user document to API response format."""
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")) if doc.get("_id") else None,
        "email": doc.get("email"),
        "username": doc.get("username"),
        "role": doc.get("role"),
    }