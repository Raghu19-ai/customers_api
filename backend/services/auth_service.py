from database.connection import users_collection
from models.users import create_user_doc, user_to_response
from utils.hash import hash_password, verify_password
from utils.jwt_handler import create_access_token, create_refresh_token, verify_token
from utils.exceptions import CustomException
from utils.logger import logger
from utils.validator import validate_password, validate_email
from bson import ObjectId


# REGISTER USER
def register_user(user_data):
    try:
        email = user_data.email.lower().strip()
        username = user_data.username.lower().strip()

        if not email or not user_data.password or not username:
            raise CustomException("Email, username and password required", 400)

        logger.info(f"Register attempt | email={email} username={username}")

        # EMAIL VALIDATION ADDED
        validate_email(email)

        # Check duplicates
        if users_collection.find_one({"email": email}):
            logger.warning(f"Duplicate email | email={email}")
            raise CustomException("Email already registered", 409)

        if users_collection.find_one({"username": username}):
            logger.warning(f"Duplicate username | username={username}")
            raise CustomException("Username already taken", 409)

        # Validate password
        validate_password(user_data.password)

        # Hash password
        hashed_password = hash_password(user_data.password)

        role = user_data.role or "user"

        user_doc = create_user_doc({
            "email": email,
            "username": username,
            "password": hashed_password,
            "role": role
        })

        result = users_collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        logger.info(f"User registered successfully | email={email}")

        return {
            "message": "User registered successfully",
            "email": email,
            "username": username,
            "role": role
        }

    except CustomException:
        raise

    except Exception:
        logger.exception("Registration failed")
        raise CustomException("Internal server error", 500)


# LOGIN USER
def login_user(email: str, password: str):
    try:
        if not email or not password:
            raise CustomException("Email and password required", 400)

        email = email.lower().strip()

        # OPTIONAL EMAIL VALIDATION
        validate_email(email)

        logger.info(f"Login attempt | email={email}")

        user = users_collection.find_one({"email": email})

        if not user or not verify_password(password, user["password"]):
            logger.warning(f"Invalid login | email={email}")
            raise CustomException("Invalid credentials", 401)

        access_token = create_access_token({
            "user": user["email"],
            "role": user["role"]
        })

        refresh_token = create_refresh_token({
            "user": user["email"],
            "type": "refresh"
        })

        logger.info(f"Login success | email={email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "role": user["role"]
        }

    except CustomException:
        raise

    except Exception:
        logger.exception("Login failed")
        raise CustomException("Internal server error", 500)


# REFRESH ACCESS TOKEN
def refresh_access_token(refresh_token: str):
    try:
        if not refresh_token:
            raise CustomException("Refresh token required", 400)

        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise CustomException("Invalid token type", 401)

        email = payload.get("user")
        if not email:
            raise CustomException("Invalid token payload", 401)

        user = users_collection.find_one({"email": email})
        if not user:
            raise CustomException("User not found", 404)

        new_access_token = create_access_token({
            "user": user["email"],
            "role": user["role"]
        })

        logger.info(f"Token refreshed | email={email}")

        return {"access_token": new_access_token}

    except CustomException:
        raise

    except Exception:
        logger.exception("Token refresh failed")
        raise CustomException("Failed to refresh token", 500)


# GET ALL USERS
def get_all_users(skip: int = 0, limit: int = 10):
    try:
        logger.info(f"Fetch users | skip={skip} limit={limit}")

        users = list(users_collection.find().skip(skip).limit(limit))

        return [user_to_response(user) for user in users]

    except Exception:
        logger.exception("Fetch users failed")
        raise CustomException("Failed to fetch users", 500)


# GET USER COUNT
def get_user_count():
    try:
        count = users_collection.count_documents({})
        logger.info(f"User count | total={count}")
        return {"count": count}

    except Exception:
        logger.exception("Count users failed")
        raise CustomException("Failed to count users", 500)


# DELETE USER
def delete_user(user_id: str):
    try:
        logger.info(f"Delete user | id={user_id}")

        from bson import ObjectId
        result = users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            logger.warning(f"User not found | id={user_id}")
            raise CustomException("User not found", 404)

        logger.info(f"User deleted | id={user_id}")

        return {"message": "User deleted successfully"}

    except CustomException:
        raise

    except Exception:
        logger.exception("Delete user failed")
        raise CustomException("Failed to delete user", 500)