import os
from pymongo import MongoClient
from bson import ObjectId


MONGO_USER = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASS = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_APP = os.getenv('MONGO_APP')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_APP}:{MONGO_PORT}/"
DB_NAME = "spreadsheet-schema"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def migrate_collections():
    print(f"Adding date_format in users...")

    result = db["users"].update_many(
        {},
        {
            "$set": {
                "date_format": "%Y-%m-%d"
            }
        }
    )

    print(f"Matched documents: {result.matched_count}")
    print(f"Updated documents: {result.modified_count}")

    print(f"Adding native_date_columns in datasets...")

    result = db["datasets"].update_many(
        {},
        {
            "$set": {
                "native_date_columns": []
            }
        }
    )

    print(f"Matched documents: {result.matched_count}")
    print(f"Updated documents: {result.modified_count}")

    print("Migration complete!")


if __name__ == "__main__":
    migrate_collections()
