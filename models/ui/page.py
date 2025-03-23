from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from dependencies.mongodb import db

class PageModel:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["pages"]
    async def create_page(self, title: str, components: List[Dict]):
        for component in components:
            component['component_id'] = str(ObjectId())
        
        new_page = {"title": title, "components": components}
        result = await self.collection.insert_one(new_page)
        return str(result.inserted_id)

    async def update_page(self, page_id: str, title: str, components: List[Dict]):
        for component in components:
            if 'component_id' not in component:
                component['component_id'] = str(ObjectId())
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$set": {"title": title, "components": components}}
        )
        return result.modified_count > 0

    async def delete_page(self, page_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(page_id)})
        return result.deleted_count > 0

    async def get_page(self, page_id: str):
        page = await self.collection.find_one({"_id": ObjectId(page_id)})
        if page:
            page["_id"] = str(page["_id"])
        return page

    async def add_component(self, page_id: str, component: Dict):
        component["component_id"] = str(ObjectId())  # Gerar um ID único para o componente
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$push": {"components": component}}
        )
        return result.modified_count > 0

    async def remove_component(self, page_id: str, component_id: str):
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$pull": {"components": {"component_id": component_id}}}
        )
        return result.modified_count > 0

    async def update_component(self, page_id: str, component_id: str, updated_component: Dict):
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id), "components.component_id": component_id},
            {"$set": {"components.$": updated_component}}
        )
        return result.modified_count > 0

page_model = PageModel(db)