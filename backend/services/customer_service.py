from sqlalchemy.orm import Session, joinedload
from models.customer import Customer
from models.address import Address
from utils.exceptions import CustomException
from utils.logger import logger
from utils.validator import validate_email   
from datetime import datetime


# CUSTOMER CSV BULK INSERT
def create_customer_from_csv(db: Session, rows: list[dict]):
    try:
        customers = []

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

            existing = db.query(Customer).filter(Customer.email == email).first()
            if existing:
                logger.debug(f"Skip row | reason=duplicate email={email}")
                continue

            customers.append(Customer(
                name=name,
                email=email,
                phone=row.get("phone"),
                company=row.get("company"),
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            ))

        db.add_all(customers)
        db.commit()

        logger.info(f"CSV customers inserted | count={len(customers)}")
        return customers

    except Exception:
        db.rollback()
        logger.exception("Customer CSV upload failed")
        raise CustomException("Customer CSV upload failed", 500)


# ADDRESS CSV BULK INSERT
def create_address_from_csv(db: Session, rows: list[dict]):
    try:
        addresses = []

        for row in rows:
            try:
                customer_id = int(row.get("customer_id"))
            except:
                logger.debug(f"Skip row | invalid customer_id data={row}")
                continue

            if not db.query(Customer).filter(Customer.id == customer_id).first():
                logger.debug(f"Skip row | customer not found id={customer_id}")
                continue

            addresses.append(Address(
                customer_id=customer_id,
                city=row.get("city"),
                state=row.get("state"),
                pincode=row.get("pincode")
            ))

        db.add_all(addresses)
        db.commit()

        logger.info(f"CSV addresses inserted | count={len(addresses)}")
        return addresses

    except Exception:
        db.rollback()
        logger.exception("Address CSV upload failed")
        raise CustomException("Address CSV upload failed", 500)


# CREATE CUSTOMER
def create_customer(db: Session, data):
    try:
        email = data.email.lower().strip()
        logger.info(f"Create customer | email={email}")

        # EMAIL VALIDATION
        validate_email(email)

        existing = db.query(Customer).filter(Customer.email == email).first()
        if existing:
            raise CustomException("Email already exists", 400)

        new_customer = Customer(
            **data.dict(exclude={"created_at", "updated_at", "email"}),
            email=email,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        logger.info(f"Customer created | id={new_customer.id}")

        return db.query(Customer).options(
            joinedload(Customer.addresses)
        ).filter(Customer.id == new_customer.id).first()

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Create customer failed")
        raise CustomException("Failed to create customer", 500)


# CREATE ADDRESS
def create_address(db: Session, data):
    try:
        logger.info(f"Create address | customer_id={data.customer_id}")

        customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not customer:
            raise CustomException("Customer not found", 404)

        new_address = Address(**data.dict())

        db.add(new_address)
        db.commit()
        db.refresh(new_address)

        return new_address

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Create address failed")
        raise CustomException("Failed to create address", 500)


# GET ALL CUSTOMERS
def get_all_customers(db: Session, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit
        logger.info(f"Fetch customers | page={page} limit={limit}")

        return (
            db.query(Customer)
            .options(joinedload(Customer.addresses))
            .offset(offset)
            .limit(limit)
            .all()
        )

    except Exception:
        logger.exception("Fetch customers failed")
        raise CustomException("Failed to fetch customers", 500)


# GET ONE CUSTOMER
def get_customer_by_id(db: Session, customer_id):
    try:
        logger.info(f"Fetch customer | id={customer_id}")

        customer = (
            db.query(Customer)
            .options(joinedload(Customer.addresses))
            .filter(Customer.id == customer_id)
            .first()
        )

        if not customer:
            raise CustomException("Customer not found", 404)

        return customer

    except CustomException:
        raise

    except Exception:
        logger.exception("Fetch customer failed")
        raise CustomException("Failed to fetch customer", 500)


# PATCH CUSTOMER
def patch_customer(db: Session, customer_id, data):
    try:
        logger.info(f"Patch customer | id={customer_id}")

        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise CustomException("Customer not found", 404)

        update_data = data.dict(exclude_unset=True)

        if "email" in update_data:
            email = update_data["email"].lower().strip()

            # EMAIL VALIDATION
            validate_email(email)

            existing = db.query(Customer).filter(
                Customer.email == email,
                Customer.id != customer_id
            ).first()

            if existing:
                raise CustomException("Email already exists", 400)

            update_data["email"] = email

        for key, value in update_data.items():
            setattr(customer, key, value)

        customer.updated_at = datetime.utcnow().isoformat()

        db.commit()
        db.refresh(customer)

        return db.query(Customer).options(
            joinedload(Customer.addresses)
        ).filter(Customer.id == customer_id).first()

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Patch customer failed")
        raise CustomException("Failed to update customer", 500)


# UPDATE CUSTOMER
def update_customer(db: Session, customer_id, data):
    try:
        logger.info(f"Update customer | id={customer_id}")

        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise CustomException("Customer not found", 404)

        email = data.email.lower().strip()

        # EMAIL VALIDATION
        validate_email(email)

        existing = db.query(Customer).filter(
            Customer.email == email,
            Customer.id != customer_id
        ).first()

        if existing:
            raise CustomException("Email already exists", 400)

        for key, value in data.dict().items():
            setattr(customer, key, value)

        customer.updated_at = datetime.utcnow().isoformat()

        db.commit()
        db.refresh(customer)

        return db.query(Customer).options(
            joinedload(Customer.addresses)
        ).filter(Customer.id == customer_id).first()

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Update customer failed")
        raise CustomException("Failed to update customer", 500)


# DELETE CUSTOMER
def delete_customer(db: Session, customer_id):
    try:
        logger.info(f"Delete customer | id={customer_id}")

        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise CustomException("Customer not found", 404)

        db.delete(customer)
        db.commit()

        logger.info(f"Customer deleted | id={customer_id}")

        return {"message": "Customer deleted successfully"}

    except CustomException:
        raise

    except Exception:
        db.rollback()
        logger.exception("Delete customer failed")
        raise CustomException("Failed to delete customer", 500)