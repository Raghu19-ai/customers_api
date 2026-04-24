"""
Role & Permission Configuration

Maps permissions to allowed roles.
Used across routers for access control.
"""

from fastapi import Depends
from utils.role_checker import get_current_user
from utils.exceptions import CustomException



# ROLE → PERMISSION MAPPING
ROLE_POLICIES = {

    # Customer
    "customer_read": ["admin", "user", "superadmin"],
    "customer_write": ["admin", "superadmin"],
    "customer_update": ["admin", "superadmin"],
    "customer_delete": ["admin","superadmin"],

    # Address
    "address_create": ["admin", "superadmin"],
    "address_upload": ["superadmin"],

    # Users
    "user_read": ["admin", "user", "superadmin"],
    "user_delete": ["superadmin"]
}



# PERMISSION CHECKER
def require_permission(permission: str):
    """
    Check if current user has required permission.
    """

    def checker(user: dict = Depends(get_current_user)):
        role = user.get("role")
        allowed_roles = ROLE_POLICIES.get(permission, [])

        if role not in allowed_roles:
            raise CustomException("Access denied", 403)

        return user

    return checker