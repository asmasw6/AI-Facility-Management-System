   
        
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL is not set in .env")

client = MongoClient(MONGODB_URL)

db = client["facility_management"]

# Collections
buildings_collection = db["buildings"]
apartments_collection = db["apartments"]
customers_collection = db["customers"]
calls_collection = db["calls"]
tickets_collection = db["tickets"]

def connect_to_mongodb():
    client.admin.command("ping")
    print("Connected to MongoDB successfully!")


def close_mongodb_connection():
     client.close()
