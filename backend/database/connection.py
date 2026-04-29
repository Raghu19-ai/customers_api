import os
from pymongo import MongoClient

# Use environment variables if available (for Docker), otherwise use defaults
MONGO_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "api_project")

client = MongoClient(MONGO_URL)

db = client[DB_NAME]
users_collection = db["users"]
customers_collection = db["customers"]
addresses_collection = db["addresses"]