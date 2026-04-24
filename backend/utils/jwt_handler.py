from datetime import datetime, timedelta
from jose import jwt, JWTError
from utils.exceptions import CustomException

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


#  Create Access Token
def create_access_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Create Refresh Token
def create_refresh_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh"
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Verify Token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise CustomException("Invalid or expired token", 401)