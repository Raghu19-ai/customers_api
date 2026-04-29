from database.connection import customers_collection, addresses_collection
from models.customer import create_customer_doc, customer_to_response
from models.address import create_address_doc, address_to_response
from utils.exceptions import CustomException
from utils.logger import logger
from utils.validator import validate_email
from datetime import datetime
from bson import ObjectId


def _get_customer_with_addresses(customer_id: str) -> dict:
    """Helper to fetch customer with their addresses."""
    customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        return None
    customer_data = customer_to_response(customer)
    addresses = list(addresses_collection.find({"customer_id": customer_id}))
    customer_data["addresses"] = [address_to_response(addr) for addr in addresses]
    return customer_data


# CUSTOMER CSV BULK INSERT
def create_customer_from_csv(rows: list[dict]):
    try:
        customers_to_insert = []

        for row in rows:
            name = row.get("name")
            email = row.get("email")

            if not name or not email:
                logger.debug(f"Skip row | reason=missing_fields data={row}")
                continue

            email = email.lower().strip()

            # EMAIL VALIDATION
            try:
                validate_email(email)
            except:
                logger.debug(f"Skip row | invalid email={email}")
                continue

            existing = customers_collection.find_one({"email": email})
            if existing:
                logger.debug(f"Skip row | reason=duplicate email={email}")
                continue

            now = datetime.utcnow().isoformat()
            customers_to_insert.append({
                "name": name,
                "email": email,
                "phone": row.get("phone"),
                "company": row.get("company"),
                "created_at": now,
                "updated_at": now
            })

        if customers_to_insert:
            result = customers_collection.insert_many(customers_to_insert)
            logger.info(f"CSV customers inserted | count={len(result.inserted_ids)}")
            return customers_to_insert
        return []

    except Exception:
        logger.exception("Customer CSV upload failed")
        raise CustomException("Customer CSV upload failed", 500)


# ADDRESS CSV BULK INSERT
def create_address_from_csv(rows: list[dict]):
    try:
        addresses_to_insert = []

        for row in rows:
            customer_id = row.get("customer_id")
            if not customer_id:
                logger.debug(f"Skip row | invalid customer_id data={row}")
                continue

            # Check if customer exists
            try:
                cid = ObjectId(customer_id) if isinstance(customer_id, str) else customer_id
                if not customers_collection.find_one({"_id": cid}):
                    logger.debug(f"Skip row | customer not found id={customer_id}")
                    continue
            except:
                logger.debug(f"Skip row | invalid customer_id format data={row}")
                continue

            addresses_to_insert.append({
                "customer_id": str(customer_id),
                "city": row.get("city"),
                "state": row.get("state"),
                "pincode": row.get("pincode")
            })

        if addresses_to_insert:
            result = addresses_collection.insert_many(addresses_to_insert)
            logger.info(f"CSV addresses inserted | count={len(result.inserted_ids)}")
            return addresses_to_insert
        return []

    except Exception:
        logger.exception("Address CSV upload failed")
        raise CustomException("Address CSV upload failed", 500)


# CREATE CUSTOMER
def create_customer(data):
    try:
        email = data.email.lower().strip()
        logger.info(f"Create customer | email={email}")

        # EMAIL VALIDATION
        validate_email(email)

        existing = customers_collection.find_one({"email": email})
        if existing:
            raise CustomException("Email already exists", 400)

        customer_doc = create_customer_doc(data.model_dump())
        result = customers_collection.insert_one(customer_doc)
        customer_doc["_id"] = result.inserted_id

        logger.info(f"Customer created | id={result.inserted_id}")

        return customer_to_response(customer_doc)

    except CustomException:
        raise

    except Exception:
        logger.exception("Create customer failed")
        raise CustomException("Failed to create customer", 500)


# CREATE ADDRESS
def create_address(data):
    try:
        logger.info(f"Create address | customer_id={data.customer_id}")

        # Check if customer exists
        try:
            cid = ObjectId(data.customer_id) if isinstance(data.customer_id, str) else data.customer_id
            customer = customers_collection.find_one({"_id": cid})
        except:
            customer = None

        if not customer:
            raise CustomException("Customer not found", 404)

        address_doc = create_address_doc({
            "customer_id": data.customer_id,
            "city": data.city,
            "state": data.state,
            "pincode": data.pincode
        })

        result = addresses_collection.insert_one(address_doc)
        address_doc["_id"] = result.inserted_id

        return address_to_response(address_doc)

    except CustomException:
        raise

    except Exception:
        logger.exception("Create address failed")
        raise CustomException("Failed to create address", 500)


# GET ALL CUSTOMERS
def get_all_customers(page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit
        logger.info(f"Fetch customers | page={page} limit={limit}")

        customers = list(customers_collection.find().skip(offset).limit(limit))

        # Fetch addresses for each customer
        result = []
        for customer in customers:
            customer_data = customer_to_response(customer)
            customer_id = str(customer["_id"])
            addresses = list(addresses_collection.find({"customer_id": customer_id}))
            customer_data["addresses"] = [address_to_response(addr) for addr in addresses]
            result.append(customer_data)

        return result

    except Exception:
        logger.exception("Fetch customers failed")
        raise CustomException("Failed to fetch customers", 500)


# GET ONE CUSTOMER
def get_customer_by_id(customer_id: str):
    try:
        logger.info(f"Fetch customer | id={customer_id}")

        customer_data = _get_customer_with_addresses(customer_id)
        if not customer_data:
            raise CustomException("Customer not found", 404)

        return customer_data

    except CustomException:
        raise

    except Exception:
        logger.exception("Fetch customer failed")
        raise CustomException("Failed to fetch customer", 500)


# PATCH CUSTOMER
def patch_customer(customer_id: str, data):
    try:
        logger.info(f"Patch customer | id={customer_id}")

        # Check customer exists
        try:
            cid = ObjectId(customer_id)
        except:
            raise CustomException("Invalid customer ID", 400)

        customer = customers_collection.find_one({"_id": cid})
        if not customer:
            raise CustomException("Customer not found", 404)

        update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}

        if "email" in update_data:
            email = update_data["email"].lower().strip()

            # EMAIL VALIDATION
            validate_email(email)

            existing = customers_collection.find_one({
                "email": email,
                "_id": {"$ne": cid}
            })

            if existing:
                raise CustomException("Email already exists", 400)

            update_data["email"] = email

        update_data["updated_at"] = datetime.utcnow().isoformat()

        customers_collection.update_one(
            {"_id": cid},
            {"$set": update_data}
        )

        return _get_customer_with_addresses(customer_id)

    except CustomException:
        raise

    except Exception:
        logger.exception("Patch customer failed")
        raise CustomException("Failed to update customer", 500)


# UPDATE CUSTOMER
def update_customer(customer_id: str, data):
    try:
        logger.info(f"Update customer | id={customer_id}")

        # Check customer exists
        try:
            cid = ObjectId(customer_id)
        except:
            raise CustomException("Invalid customer ID", 400)

        customer = customers_collection.find_one({"_id": cid})
        if not customer:
            raise CustomException("Customer not found", 404)

        email = data.email.lower().strip()

        # EMAIL VALIDATION
        validate_email(email)

        existing = customers_collection.find_one({
            "email": email,
            "_id": {"$ne": cid}
        })

        if existing:
            raise CustomException("Email already exists", 400)

        update_data = data.model_dump()
        update_data["email"] = email
        update_data["updated_at"] = datetime.utcnow().isoformat()

        customers_collection.update_one(
            {"_id": cid},
            {"$set": update_data}
        )

        return _get_customer_with_addresses(customer_id)

    except CustomException:
        raise

    except Exception:
        logger.exception("Update customer failed")
        raise CustomException("Failed to update customer", 500)


# DELETE CUSTOMER
def delete_customer(customer_id: str):
    try:
        logger.info(f"Delete customer | id={customer_id}")

        try:
            cid = ObjectId(customer_id)
        except:
            raise CustomException("Invalid customer ID", 400)

        # Delete customer
        result = customers_collection.delete_one({"_id": cid})
        if result.deleted_count == 0:
            raise CustomException("Customer not found", 404)

        # Delete associated addresses
        addresses_collection.delete_many({"customer_id": customer_id})

        logger.info(f"Customer deleted | id={customer_id}")

        return {"message": "Customer deleted successfully"}

    except CustomException:
        raise

    except Exception:
        logger.exception("Delete customer failed")
        raise CustomException("Failed to delete customer", 500)