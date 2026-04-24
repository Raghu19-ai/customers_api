import re
from fastapi import HTTPException


#  PASSWORD VALIDATION
def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Must contain uppercase letter")

    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Must contain lowercase letter")

    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="Must contain number")

    if not re.search(r"[!@#$%^&*]", password):
        raise HTTPException(status_code=400, detail="Must contain special character")


# EMAIL VALIDATION
def validate_email(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if not re.match(pattern, email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )