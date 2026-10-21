import os
from pymongo import MongoClient
from bson import ObjectId


MONGO_USER = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASS = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_APP = os.getenv('MONGO_APP')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_APP}:{MONGO_PORT}/"
DB_NAME = "spreadsheet-schema"

# The ID of the user who "owns" the existing legacy data
TARGET_OWNER_ID = ObjectId("69814e9c029aa44279b357a6") 
TARGET_CREATOR_ID = ObjectId("69814ece029aa44279b357a8")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def migrate_collections():
    print(f"Migrating fields...")
        
    # Update all documents that don't have an owner_id yet
    result = db["fields"].update_many(
        {"owner_id": {"$exists": False}},  # Only target old docs
        {
            "$set": {
                "owner_id": TARGET_OWNER_ID,
                "scope": "TEAM"
            }
        }
    )
    db["fields"].create_index([("owner_id", 1), ("scope", 1)])
    
    print(f" -> Updated {result.modified_count} documents in fields.")
    
    collections = ["templates", "workbooks"]

    for collection in collections:

        print(f"Migrating {collection}...")
        
        # Update all documents that don't have an owner_id yet
        result = db[collection].update_many(
            {"owner_id": {"$exists": False}},  # Only target old docs
            {
                "$set": {
                    "owner_id": TARGET_OWNER_ID,
                    "scope": "TEAM",
                    "fields.$[f].owner_id": TARGET_OWNER_ID,
                    "fields.$[f].scope": "TEAM"
                }
            },
            array_filters=[{"f": {"$exists": True}}] # Target every element in 'fields'
        )
        
        print(f" -> Updated {result.modified_count} documents in {collection}.")

        # --- ADDING INDEXES ---
        # This ensures your Rio app stays fast after the migration
        print("Creating indexes...")
        db[collection].create_index([("owner_id", 1), ("scope", 1)])

    print("Migration complete!")


if __name__ == "__main__":
    migrate_collections()