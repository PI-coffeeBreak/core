from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from dependencies.mongodb import db
from utils.mongoserializer import to_object_id, from_mongo

class PageService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["pages"]

    async def create_page(self, title: str, components: List[Dict]) -> str:
        for component in components:
            component['component_id'] = str(ObjectId())

        new_page = {"title": title, "components": components}
        result = await self.collection.insert_one(new_page)
        return str(result.inserted_id)

    async def update_page(self, page_id: str, title: str, components: List[Dict]) -> bool:
        for component in components:
            if 'component_id' not in component:
                component['component_id'] = str(ObjectId())
        result = await self.collection.update_one(
            {"_id": to_object_id(page_id)},
            {"$set": {"title": title, "components": components}}
        )
        return result.modified_count > 0

    async def delete_page(self, page_id: str) -> bool:
        result = await self.collection.delete_one({"_id": to_object_id(page_id)})
        return result.deleted_count > 0

    async def list_pages(self):
        cursor = self.collection.find()
        pages = []
        async for page in cursor:
            pages.append(from_mongo(page))
        return pages

    async def get_page(self, page_id: str) -> Dict:
        page = await self.collection.find_one({"_id": to_object_id(page_id)})
        return from_mongo(page) if page else None

    async def add_component(self, page_id: str, component: Dict) -> bool:
        component["component_id"] = str(ObjectId())  # Generate a unique ID for the component
        result = await self.collection.update_one(
            {"_id": to_object_id(page_id)},
            {"$push": {"components": component}}
        )
        return result.modified_count > 0

    async def remove_component(self, page_id: str, component_id: str) -> bool:
        result = await self.collection.update_one(
            {"_id": to_object_id(page_id)},
            {"$pull": {"components": {"component_id": component_id}}}
        )
        return result.modified_count > 0

    async def update_component(self, page_id: str, component_id: str, updated_component: Dict) -> bool:
        result = await self.collection.update_one(
            {"_id": to_object_id(page_id), "components.component_id": component_id},
            {"$set": {"components.$": updated_component}}
        )
        return result.modified_count > 0

# Initialize the service with the database dependency
page_service = PageService(db)
