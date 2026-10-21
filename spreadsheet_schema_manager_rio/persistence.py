from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
import uniserde
from uniserde import ObjectId
from typing import Type

from .data_models import *
from . import constants

SERDE = uniserde.BsonSerde()
COL_TEAMS = "teams"
COL_USERS = "users"


class PersistenceBase:
    def __init__(
        self,
        collection: AsyncCollection,
    ) -> None:
        self.collection = collection

    def get_scope_filter(self, user: AppUser) -> dict:
        owner_id, scope = user.get_owner()
        return {
            "owner_id": owner_id,
            "scope": scope.name
        }
    
    async def update_one_str(self, id: ObjectId, key: str, value: str) -> None:
        query_filter = {"_id": id}
        update_operation = { '$set' : 
            {key: value}
        }
        await self.collection.update_one(query_filter, update_operation)
    
    async def delete_one(self, id: ObjectId) -> None:
        await self.collection.delete_one({"_id": id})
        
    async def delete_all(self, user: AppUser) -> None:
        query_filter = self.get_scope_filter(user)
        await self.collection.delete_many(query_filter)


class FieldPersistence(PersistenceBase):
    def __init__(
        self,
        collection: AsyncCollection,
    ) -> None:
        super().__init__(collection)
    
    async def get_all(self, user: AppUser) -> list[Field]:
        fields: list[Field] = []
        query_filter = self.get_scope_filter(user)
        results = self.collection.find(query_filter)
        async for result in results:
            fields.append(SERDE.from_bson(constants.FIELD_TYPE_DICT[result["type"]], result))
        
        type_order = {t: index for index, t in enumerate(constants.FIELD_TYPES)}
        sorted_fields = sorted(fields, key=lambda f: (f.group == "", f.group, type_order[f.__class__], f.header))
        return sorted_fields
    
    async def get_one(self, id: ObjectId) -> Field:
        result = await self.collection.find_one({"_id": id})
        if result is None:
            return None
        return SERDE.from_bson(constants.FIELD_TYPE_DICT[result["type"]], result)

    async def find_one_by_id(self, param_id: str) -> Field:
        return await self.get_one(ObjectId(param_id))

    async def find_one_by_header(self, user: AppUser, header: str) -> Template:
        query_filter = self.get_scope_filter(user)
        query_filter["header"] = header
        result = await self.collection.find_one(query_filter)
        if result is None:
            return None
        return SERDE.from_bson(constants.FIELD_TYPE_DICT[result["type"]], result)

    async def upsert_one(self, data: Field) -> None:
        await self.collection.replace_one(
            {"_id": data.id},
            SERDE.as_bson(data),
            upsert=True,
        )
    
    async def update_header(self, id: ObjectId, header: str) -> None:
        await self.update_one_str(id, "header", header)

    async def insert_one(self, data: Field) -> ObjectId:
        data_bson = SERDE.as_bson(data)
        del data_bson["_id"]
        result = await self.collection.insert_one(
            data_bson,
        )
        return result.inserted_id


class WorkbookPersistence(PersistenceBase):
    def __init__(
        self,
        collection: AsyncCollection,
        workbook_type: Type[Template],
    ) -> None:
        super().__init__(collection)
        self.workbook_type = workbook_type
    
    async def get_all(self, user: AppUser) -> list[Template]:
        workbooks: list[Template] = []
        query_filter = self.get_scope_filter(user)
        results = self.collection.find(query_filter)
        async for result in results:
            workbooks.append(SERDE.from_bson(self.workbook_type, result))
        return workbooks
    
    async def get_one(self, id: ObjectId) -> Template:
        result = await self.collection.find_one({"_id": id})
        if result is None:
            return None
        return SERDE.from_bson(self.workbook_type, result)

    async def find_one_by_id(self, param_id: str) -> Template:
        return await self.get_one(ObjectId(param_id))

    async def find_one_by_name(self, user: AppUser, name: str) -> Template:
        query_filter = self.get_scope_filter(user)
        query_filter["name"] = name
        result = await self.collection.find_one(query_filter)
        if result is None:
            return None
        return SERDE.from_bson(self.workbook_type, result)

    async def upsert_one(self, data: Template) -> None:
        await self.collection.replace_one(
            {"_id": data.id},
            SERDE.as_bson(data),
            upsert=True,
        )

    async def update_one_name(self, id: ObjectId, name: str) -> None:
        await self.update_one_str(id, "name", name)

    async def insert_one(self, data: Template) -> ObjectId:
        data_bson = SERDE.as_bson(data)
        del data_bson["_id"]
        result = await self.collection.insert_one(
            data_bson,
        )
        return result.inserted_id


class DatasetPersistence(PersistenceBase):
    def __init__(
        self,
        collection: AsyncCollection,
    ) -> None:
        super().__init__(collection)

    def get_scope_filter(self, user: AppUser) -> dict:
        query_filter = super().get_scope_filter(user)
        query_filter["creator_id"] = user.id
        return query_filter
    
    async def get_all(self, user: AppUser) -> list[Dataset]:
        datasets: list[Dataset] = []
        query_filter = self.get_scope_filter(user)
        results = self.collection.find(query_filter)
        async for result in results:
            datasets.append(SERDE.from_bson(Dataset, result))
        return datasets
    
    async def get_one(self, id: ObjectId) -> Dataset:
        result = await self.collection.find_one({"_id": id})
        if result is None:
            return None
        return SERDE.from_bson(Dataset, result)

    async def find_one_by_id(self, param_id: str) -> Dataset:
        return await self.get_one(ObjectId(param_id))

    async def find_one_by_name(self, user: AppUser, name: str) -> Dataset:
        query_filter = self.get_scope_filter(user)
        query_filter["name"] = name
        result = await self.collection.find_one(query_filter)
        if result is None:
            return None
        return SERDE.from_bson(Dataset, result)

    async def upsert_one(self, data: Dataset) -> None:
        await self.collection.replace_one(
            {"_id": data.id},
            SERDE.as_bson(data),
            upsert=True,
        )

    async def update_one_name(self, id: ObjectId, name: str) -> None:
        await self.update_one_str(id, "name", name)

    async def insert_one(self, data: Dataset) -> ObjectId:
        data_bson = SERDE.as_bson(data)
        del data_bson["_id"]
        result = await self.collection.insert_one(
            data_bson,
        )
        return result.inserted_id


class Persistence:
    def __init__(
        self,
        mongodb_connection_string: str,
        database_name: str,
    ) -> None:
        self.client = AsyncMongoClient(mongodb_connection_string)
        self.db = self.client[database_name]
        self._field_pers = FieldPersistence(
            self.db["fields"]
        )
        self._template_pers = WorkbookPersistence(
            self.db["templates"],
            Template,
        )
        self._workbook_pers = WorkbookPersistence(
            self.db["workbooks"],
            Workbook,
        )
        self._dataset_pers = DatasetPersistence(
            self.db["datasets"]
        )
    
    def get_field(self) -> FieldPersistence:
        return self._field_pers

    def get_template(self) -> WorkbookPersistence:
        return self._template_pers
    
    def get_workbook(self) -> WorkbookPersistence:
        return self._workbook_pers

    def get_dataset(self) -> DatasetPersistence:
        return self._dataset_pers


    async def find_user_by_email(self, email: str) -> AppUser:
        result = await self.db[COL_USERS].find_one({"email": email})
        if result is None:
            return None
        return SERDE.from_bson(AppUser, result)
    
    async def insert_user(self, data: AppUser) -> ObjectId:
        data_bson = SERDE.as_bson(data)
        del data_bson["_id"]
        result = await self.db[COL_USERS].insert_one(
            data_bson,
        )
        return result.inserted_id
    
    async def upsert_user(self, data: AppUser) -> None:
        await self.db[COL_USERS].replace_one(
            {"_id": data.id},
            SERDE.as_bson(data),
            upsert=True,
        )
        