import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve MongoDB connection details from .env
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Ensure variables are loaded correctly
if not MONGO_URI or not MONGO_DB_NAME:
    raise ValueError("MongoDB connection details are missing in the .env file")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database(MONGO_DB_NAME)

# Define collection names
meal_plans_collection = db["meal_plans"]
