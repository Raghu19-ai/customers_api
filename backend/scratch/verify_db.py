from database.connection import db, users_collection, customers_collection, addresses_collection

def test_connection():
    try:
        # Test MongoDB connection by pinging the server
        db.client.admin.command('ping')
        print("MongoDB connection successful!")

        # Check document counts
        user_count = users_collection.count_documents({})
        customer_count = customers_collection.count_documents({})
        address_count = addresses_collection.count_documents({})

        print(f"Collection check:")
        print(f"   - Users: {user_count} documents")
        print(f"   - Customers: {customer_count} documents")
        print(f"   - Addresses: {address_count} documents")

    except Exception as e:
        print(f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection()
