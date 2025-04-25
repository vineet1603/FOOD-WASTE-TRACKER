from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, date

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "food_waste_tracker"
COLLECTION_NAME = "waste_entries"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
waste_collection = db[COLLECTION_NAME]

def unit_to_kg(quantity, unit):
    conversion_factors = {
        "g": 0.001,
        "kg": 1,
        "mg": 0.000001,
        "lb": 0.453592,
        "oz": 0.0283495,
        "ltr": 1,
        "ml": 0.001
    }
    return quantity * conversion_factors.get(unit, 1)

def add_waste_entry_to_db(food_item, category, quantity, unit, quantity_kg, date, reason, notes):
    entry = {
        "food_item": food_item,
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "quantity_kg": quantity_kg,
        "date": datetime.combine(date, datetime.min.time()),  # 👈 fixed error
        "reason": reason,
        "notes": notes,
        "entry_timestamp": datetime.utcnow()
    }
    result = waste_collection.insert_one(entry)
    return str(result.inserted_id)

def get_all_waste_entries():
    return list(waste_collection.find())
