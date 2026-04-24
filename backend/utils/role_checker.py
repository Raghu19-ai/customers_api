from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from utils.jwt_handler import verify_token
from utils.exceptions import CustomException

security = HTTPBearer()


# Get current user from token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)

    # Allow only access tokens
    if payload.get("type") != "access":
        raise CustomException("Invalid access token", 401)

    return payload


# Role-based access control
def require_role(allowed_roles: list):
    def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        return user

    return checker