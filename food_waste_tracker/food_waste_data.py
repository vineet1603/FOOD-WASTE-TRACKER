from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from datetime import datetime

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["food_waste_tracker"]
collection = db["waste_entries"]

# Convert unit to kg
def convert_to_kg(quantity, unit):
    factors = {
        "kg": 1,
        "lbs": 0.453592,
        "servings": 0.25,
        "items": 0.15
    }
    return quantity * factors.get(unit.lower(), 1)

# Add a new entry to MongoDB
def add_waste_entry(_, food_item, category, quantity, unit, date, reason, notes):
    quantity_kg = convert_to_kg(quantity, unit)
    dt = date if isinstance(date, datetime) else datetime.combine(date, datetime.min.time())

    entry = {
        "food_item": food_item,
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "quantity_kg": quantity_kg,
        "date": dt,
        "reason": reason,
        "notes": notes,
        "entry_timestamp": datetime.utcnow()
    }
    collection.insert_one(entry)

# Load all entries from MongoDB as DataFrame
def initialize_data():
    data = list(collection.find())
    for item in data:
        item["_id"] = str(item["_id"])
    df = pd.DataFrame(data)

    # Ensure date is datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors='coerce')
    else:
        df["date"] = pd.NaT

    return df

# Get summary stats
def get_stats(df):
    if df.empty:
        return 0, 0, "N/A"

    total = df["quantity_kg"].sum()
    daily_avg = df.groupby("date")["quantity_kg"].sum().mean()
    top_cat = df.groupby("category")["quantity_kg"].sum().idxmax()
    return total, daily_avg, top_cat

# Delete entry by Mongo ID
def delete_data_by_id(id_str):
    collection.delete_one({"_id": ObjectId(id_str)})

# Return raw list of all data (for tables)
def get_all_data():
    return list(collection.find())
