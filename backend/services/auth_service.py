from sqlalchemy.orm import Session
from models.users import User

from utils.hash import hash_password, verify_password
from utils.jwt_handler import create_access_token, create_refresh_token, verify_token
from utils.exceptions import CustomException
from utils.logger import logger
from utils.validator import validate_password, validate_email   


# REGISTER USER
def register_user(db: Session, user_data):
    try:
        email = user_data.email.lower().strip()
        username = user_data.username.lower().strip()

        if not email or not user_data.password or not username:
            raise CustomException("Email, username and password required", 400)

        logger.info(f"Register attempt | email={email} username={username}")

        # EMAIL VALIDATION ADDED
        validate_email(email)

        # Check duplicates
        if db.query(User).filter(User.email == email).first():
            logger.warning(f"Duplicate email | email={email}")
            raise CustomException("Email already registered", 409)

        if db.query(User).filter(User.username == username).first():
            logger.warning(f"Duplicate username | username={username}")
            raise CustomException("Username already taken", 409)

        # Validate password
        validate_password(user_data.password)

        # Hash password
        hashed_password = hash_password(user_data.password)

        role = user_data.role or "user"

        user = User(
            email=email,
            username=username,
            password=hashed_password,
            role=role
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User registered successfully | email={email}")

        return {
            "message": "User registered successfully",
            "email": user.email,
            "username": user.username,
            "role": user.role
        }

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Registration failed")
        raise CustomException("Internal server error", 500)


# LOGIN USER
def login_user(db: Session, email: str, password: str):
    try:
        if not email or not password:
            raise CustomException("Email and password required", 400)

        email = email.lower().strip()

        # OPTIONAL EMAIL VALIDATION 
        validate_email(email)

        logger.info(f"Login attempt | email={email}")

        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password):
            logger.warning(f"Invalid login | email={email}")
            raise CustomException("Invalid credentials", 401)

        access_token = create_access_token({
            "user": user.email,
            "role": user.role
        })

        refresh_token = create_refresh_token({
            "user": user.email,
            "type": "refresh"
        })

        logger.info(f"Login success | email={email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "role": user.role
        }

    except CustomException:
        raise

    except Exception:
        logger.exception("Login failed")
        raise CustomException("Internal server error", 500)


# REFRESH ACCESS TOKEN
def refresh_access_token(db: Session, refresh_token: str):
    try:
        if not refresh_token:
            raise CustomException("Refresh token required", 400)

        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise CustomException("Invalid token type", 401)

        email = payload.get("user")
        if not email:
            raise CustomException("Invalid token payload", 401)

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise CustomException("User not found", 404)

        new_access_token = create_access_token({
            "user": user.email,
            "role": user.role
        })

        logger.info(f"Token refreshed | email={email}")

        return {"access_token": new_access_token}

    except CustomException:
        raise

    except Exception:
        logger.exception("Token refresh failed")
        raise CustomException("Failed to refresh token", 500)


# GET ALL USERS
def get_all_users(db: Session, skip: int = 0, limit: int = 10):
    try:
        logger.info(f"Fetch users | skip={skip} limit={limit}")

        users = db.query(User).offset(skip).limit(limit).all()

        return [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
            for user in users
        ]

    except Exception:
        logger.exception("Fetch users failed")
        raise CustomException("Failed to fetch users", 500)


# GET USER COUNT
def get_user_count(db: Session):
    try:
        count = db.query(User).count()
        logger.info(f"User count | total={count}")
        return {"count": count}

    except Exception:
        logger.exception("Count users failed")
        raise CustomException("Failed to count users", 500)


# DELETE USER
def delete_user(db: Session, user_id: int):
    try:
        logger.info(f"Delete user | id={user_id}")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"User not found | id={user_id}")
            raise CustomException("User not found", 404)

        db.delete(user)
        db.commit()

        logger.info(f"User deleted | id={user_id}")

        return {"message": "User deleted successfully"}

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Delete user failed")
        raise CustomException("Failed to delete user", 500)