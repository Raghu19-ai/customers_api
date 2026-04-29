from fastapi import APIRouter, Depends, UploadFile, File, Request, status
import csv, io

from schemas.customer_schemas import CustomerCreate, CustomerResponse, CustomerUpdate
from schemas.address_schema import AddressCreate, AddressResponse as FullAddressResponse

from services.customer_service import (
    create_customer,
    create_address,
    get_all_customers,
    get_customer_by_id,
    patch_customer,
    update_customer,
    delete_customer,
    create_customer_from_csv,
    create_address_from_csv
)

from utils.roles import require_permission
from utils.logger import logger
from utils.exceptions import CustomException
from utils.rate_limiter import limiter


router = APIRouter(prefix="/customers", tags=["Customers"])
addr_router = APIRouter(prefix="/addresses", tags=["Addresses"])


# CUSTOMER CSV UPLOAD
@router.post(
    "/upload",
    summary="Bulk Upload Customers",
    description="Upload multiple customers at once via CSV file.",
    responses={
        200: {"description": "Upload successful"},
        400: {"description": "Invalid file format"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("2/minute")
def upload_customers(
    request: Request,
    file: UploadFile = File(...),
    user=Depends(require_permission("customer_write"))
):
    logger.info(f"Customer CSV upload | user={user.get('user')}")

    if not file.filename.endswith(".csv"):
        raise CustomException("Only CSV files allowed", 400)

    try:
        rows = list(csv.DictReader(io.StringIO(file.file.read().decode("utf-8"))))
        customers = create_customer_from_csv(rows)

        logger.info(f"Customers uploaded successfully | count={len(customers)}")

        return {
            "message": "Customer upload successful",
            "created": len(customers)
        }

    except Exception:
        logger.exception("Customer CSV upload failed")
        raise CustomException("CSV upload failed", 500)


# CREATE CUSTOMER
@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Single Customer",
    description="Create a new customer profile with detailed information.",
    responses={
        201: {"model": CustomerResponse, "description": "Customer created successfully"},
        400: {"description": "Validation error or email exists"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def create_customer_api(
    request: Request,
    data: CustomerCreate,
    user=Depends(require_permission("customer_write"))
):
    logger.info(f"Create customer | user={user.get('user')} | email={data.email}")
    return create_customer(data)


# GET ALL CUSTOMERS
@router.get(
    "/",
    response_model=list[CustomerResponse],
    summary="Get Paginated Customers",
    description="Fetch a list of customers with support for page and limit parameters.",
    responses={
        200: {"model": list[CustomerResponse], "description": "List of customers retrieved"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("10/minute")
def get_all(
    request: Request,
    page: int = 1,
    limit: int = 5,
    user=Depends(require_permission("customer_read"))
):
    logger.info(f"Fetch customers | user={user.get('user')} | page={page} limit={limit}")

    if page < 1 or limit < 1:
        raise CustomException("Invalid pagination values", 400)

    limit = min(limit, 100)
    return get_all_customers(page, limit)


# GET ONE CUSTOMER
@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get Customer Details",
    description="Fetch full details of a single customer by ID.",
    responses={
        200: {"model": CustomerResponse, "description": "Customer details retrieved"},
        401: {"description": "Unauthorized"},
        404: {"description": "Customer not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("10/minute")
def get_one(
    request: Request,
    customer_id: str,
    user=Depends(require_permission("customer_read"))
):
    logger.info(f"Fetch customer | id={customer_id} | user={user.get('user')}")
    return get_customer_by_id(customer_id)



# PATCH CUSTOMER
@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Partial Update Customer",
    description="Update specific fields of a customer record.",
    responses={
        200: {"model": CustomerResponse, "description": "Customer updated successfully"},
        400: {"description": "Invalid data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Customer not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def patch(
    request: Request,
    customer_id: str,
    data: CustomerUpdate,
    user=Depends(require_permission("customer_update"))
):
    logger.info(f"Patch customer | id={customer_id} | user={user.get('user')}")

    try:
        return patch_customer(customer_id, data)

    except Exception:
        logger.exception("Customer patch failed")
        raise CustomException("Patch failed", 500)


# UPDATE CUSTOMER
@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Full Update Customer",
    description="Replace an entire customer record.",
    responses={
        200: {"model": CustomerResponse, "description": "Customer replaced successfully"},
        400: {"description": "Validation error"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Customer not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def update(
    request: Request,
    customer_id: str,
    data: CustomerCreate,
    user=Depends(require_permission("customer_update"))
):
    logger.info(f"Update customer | id={customer_id} | user={user.get('user')}")

    try:
        return update_customer(customer_id, data)

    except Exception:
        logger.exception("Customer update failed")
        raise CustomException("Update failed", 500)


# DELETE CUSTOMER
@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Customer",
    description="Remove a customer and all their associated addresses.",
    responses={
        200: {"description": "Customer deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Customer not found"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def remove(
    request: Request,
    customer_id: str,
    user=Depends(require_permission("customer_delete"))
):
    logger.warning(f"Delete customer | id={customer_id} | user={user.get('user')}")

    try:
        return delete_customer(customer_id)

    except Exception:
        logger.exception("Delete failed")
        raise CustomException("Delete failed", 500)


# ADDRESS CSV UPLOAD
@addr_router.post(
    "/upload",
    summary="Bulk Upload Addresses",
    description="Upload customer addresses via CSV file.",
    responses={
        200: {"description": "Upload successful"},
        400: {"description": "Invalid file format"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("2/minute")
def upload_addresses(
    request: Request,
    file: UploadFile = File(...),
    user=Depends(require_permission("address_upload"))
):
    logger.info(f"Address CSV upload | user={user.get('user')}")

    if not file.filename.endswith(".csv"):
        raise CustomException("Only CSV files allowed", 400)

    try:
        rows = list(csv.DictReader(io.StringIO(file.file.read().decode("utf-8"))))
        addresses = create_address_from_csv(rows)

        logger.info(f"Addresses uploaded | count={len(addresses)}")

        return {
            "message": "Address upload successful",
            "created": len(addresses)
        }

    except Exception:
        logger.exception("Address CSV upload failed")
        raise CustomException("CSV upload failed", 500)


# CREATE ADDRESS
@addr_router.post(
    "/",
    response_model=FullAddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Customer Address",
    description="Link a new address to an existing customer record.",
    responses={
        201: {"model": FullAddressResponse, "description": "Address added successfully"},
        400: {"description": "Validation error or customer missing"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
@limiter.limit("5/minute")
def add_address(
    request: Request,
    data: AddressCreate,
    user=Depends(require_permission("address_create"))
):
    logger.info(f"Add address | customer_id={data.customer_id} | user={user.get('user')}")
    return create_address(data)