"""
Authentication Router

Handles all authentication-related APIs:
- User registration
- User login
- Token refresh
- Admin user management

Uses permission-based access control.
"""

from fastapi import APIRouter, Depends, Request, status, Body

from schemas.users_schema import UserCreate, UserLogin, UserResponse, LoginResponse

from services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    get_all_users,
    get_user_count,
    delete_user
)

from utils.logger import logger
from utils.rate_limiter import limiter
from utils.roles import require_permission


router = APIRouter(prefix="/auth", tags=["Auth"])


# REGISTER USER
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register New User",
    description="Creates a new user account with specified role.",
    responses={
        201: {"model": UserResponse, "description": "User created successfully"},
        400: {"description": "Invalid data or email already exists"},
        409: {"description": "Conflict: Email or Username already taken"},
        429: {"description": "Too many registration attempts"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("3/minute")
def register(request: Request, user: UserCreate):
    logger.info(f"Register API called | email={user.email}")
    return register_user(user)


# LOGIN USER
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    summary="User Login",
    description="Authenticates user and returns Access and Refresh tokens.",
    responses={
        200: {"model": LoginResponse, "description": "Login successful"},
        400: {"description": "Missing email or password"},
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many login attempts"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def login(request: Request, user: UserLogin):
    logger.info(f"Login API called | email={user.email}")
    return login_user(user.email, user.password)



# REFRESH TOKEN (FIXED)
@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Generates a new access token using a valid refresh token provided in the request body.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("10/minute")
def refresh_token(
    request: Request,
    token: str = Body(...)
):
    logger.info("Token refresh requested")
    return refresh_access_token(token)



# GET ALL USERS
@router.get(
    "/users", 
    status_code=status.HTTP_200_OK,
    summary="Get All Users",
    description="Fetch a paginated list of all users. Required: user_read permission.",
    responses={
        200: {"description": "List of users retrieved"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden: Insufficient permissions"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("10/minute")
def get_users(
    request: Request,
    user=Depends(require_permission("user_read"))
):
    logger.info(f"Fetch users API called")
    return get_all_users()


# USER COUNT
@router.get(
    "/users/count", 
    status_code=status.HTTP_200_OK,
    summary="Get User Count",
    description="Get total number of users in the system.",
    responses={
        200: {"description": "Count retrieved"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    }
)
@limiter.limit("10/minute")
def get_count(
    request: Request,
    user=Depends(require_permission("user_read"))
):
    logger.info("User count API called")
    return get_user_count()


# DELETE USER
@router.delete(
    "/users/{user_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete User",
    description="Deletes a user account by ID. Required: user_delete permission.",
    responses={
        200: {"description": "User deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def remove_user(
    request: Request,
    user_id: str,
    user=Depends(require_permission("user_delete"))
):
    logger.warning(f"Delete user API called | user_id={user_id}")
    return delete_user(user_id)