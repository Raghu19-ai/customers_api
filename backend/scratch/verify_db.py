from sqlalchemy import text
from database.connection import engine, SessionLocal

def test_connection():
    try:
        # Try to connect and execute a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")

        # Check if tables exist
        with SessionLocal() as session:
            # Querying from models to check if tables are mapped
            from models.users import User
            from models.customer import Customer
            from models.address import Address
            
            user_count = session.query(User).count()
            customer_count = session.query(Customer).count()
            address_count = session.query(Address).count()
            
            print(f"Table check:")
            print(f"   - Users: {user_count} records")
            print(f"   - Customers: {customer_count} records")
            print(f"   - Addresses: {address_count} records")
            
    except Exception as e:
        print(f" Database connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection()
