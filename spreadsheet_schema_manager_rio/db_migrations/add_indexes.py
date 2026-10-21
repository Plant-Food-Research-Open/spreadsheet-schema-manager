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
    print(f"Adding index on fields...")
    name = db["fields"].create_index([("owner_id", 1), ("scope", 1), ("header", 1)])
    print(f"Created index: {name}")

    print(f"Adding index on templates...")
    name = db["templates"].create_index([("owner_id", 1), ("scope", 1), ("name", 1)])
    print(f"Created index: {name}")

    print(f"Adding index on workbooks...")
    name = db["workbooks"].create_index([("owner_id", 1), ("scope", 1), ("name", 1)])
    print(f"Created index: {name}")

    print(f"Adding index on datasets...")
    name = db["datasets"].create_index([("owner_id", 1), ("scope", 1), ("creator_id", 1), ("name", 1)])
    print(f"Created index: {name}")

    print(f"Adding unique index on users...")
    name = db["users"].create_index([("email", 1)], unique=True)
    print(f"Created index: {name}")

    print("Indexing complete!")


if __name__ == "__main__":
    migrate_collections()
