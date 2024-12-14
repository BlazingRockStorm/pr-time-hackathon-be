import os
from typing import Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

from models import PressRelease

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)

db = client.get_database("press_release_db")
press_releases_collection = db["press_releases"]

def change_objectid_to_str(result):
    result["_id"] = str(result["_id"])
    return result

def insert_press(press: Dict):
    result = press_releases_collection.insert_one(press)
    return str(result.inserted_id)

def fetch_all_presses() -> List[Dict]:
    results = press_releases_collection.find()
    return [change_objectid_to_str(result) for result in results]

def fetch_press_by_id(press_id: str):
    object_id = ObjectId(press_id)
    result = press_releases_collection.find_one({"_id": object_id})
    if result:
        return change_objectid_to_str(result)
    return None
