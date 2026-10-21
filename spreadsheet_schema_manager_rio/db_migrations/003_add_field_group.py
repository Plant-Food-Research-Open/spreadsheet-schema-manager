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
    print(f"Adding field group in fields...")

    query_filter = {}
    update_operation = {
        "$set": {"group": ""}
    }

    result = db["fields"].update_many(query_filter, update_operation)
    print(f"Matched documents: {result.matched_count}")
    print(f"Updated documents: {result.modified_count}")

    print(f"Adding field group in workbooks...")

    query_filter = {}
    update_operation = {
        "$set": { "fields.$[elem].group": "" }
    }

    result = db["workbooks"].update_many(
        query_filter, 
        update_operation,
        array_filters=[{ "elem": { "$exists": True } }]
    )
    print(f"Matched documents: {result.matched_count}")
    print(f"Updated documents: {result.modified_count}")
    
    print(f"Adding field group in templates...")

    query_filter = {}
    update_operation = {
        "$set": { "fields.$[elem].group": "" }
    }

    result = db["templates"].update_many(
        query_filter, 
        update_operation,
        array_filters=[{ "elem": { "$exists": True } }]
    )
    print(f"Matched documents: {result.matched_count}")
    print(f"Updated documents: {result.modified_count}")
        
    print("Migration complete!")


if __name__ == "__main__":
    migrate_collections()