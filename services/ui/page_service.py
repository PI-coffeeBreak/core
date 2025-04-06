from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict
from dependencies.mongodb import db
import logging

logger = logging.getLogger("coffeebreak.core")


class PageService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["pages"]
        logger.debug(
            f"Initialized PageService with collection: {self.collection.name}")

    async def create_page(self, title: str, components: List[Dict]) -> str:
        for component in components:
            component['component_id'] = str(ObjectId())

        new_page = {"title": title, "components": components}
        result = await self.collection.insert_one(new_page)
        logger.debug(f"Created new page with ID: {result.inserted_id}")
        return str(result.inserted_id)

    async def update_page(self, page_id: str, title: str, components: List[Dict]) -> bool:
        for component in components:
            if 'component_id' not in component:
                component['component_id'] = str(ObjectId())
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$set": {"title": title, "components": components}}
        )
        logger.debug(
            f"Updated page {page_id}, modified count: {result.modified_count}")
        return result.modified_count > 0

    async def delete_page(self, page_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(page_id)})
        logger.debug(
            f"Deleted page {page_id}, deleted count: {result.deleted_count}")
        return result.deleted_count > 0

    async def list_pages(self):
        logger.debug("Listing all pages")
        cursor = self.collection.find()
        pages = []
        async for page in cursor:
            page["_id"] = str(page["_id"])
            pages.append(page)
        logger.debug(f"Found {len(pages)} pages")
        return pages

    async def get_page(self, page_id: str) -> Dict:
        logger.debug(f"Getting page with ID: {page_id}")
        page = await self.collection.find_one({"_id": ObjectId(page_id)})
        if page:
            page["_id"] = str(page["_id"])
            logger.debug(f"Found page: {page['title']}")
        else:
            logger.debug(f"Page {page_id} not found")
        return page

    async def add_component(self, page_id: str, component: Dict) -> bool:
        component["component_id"] = str(ObjectId())
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$push": {"components": component}}
        )
        logger.debug(
            f"Added component to page {page_id}, modified count: {result.modified_count}")
        return result.modified_count > 0

    async def remove_component(self, page_id: str, component_id: str) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id)},
            {"$pull": {"components": {"component_id": component_id}}}
        )
        logger.debug(
            f"Removed component {component_id} from page {page_id}, modified count: {result.modified_count}")
        return result.modified_count > 0

    async def update_component(self, page_id: str, component_id: str, updated_component: Dict) -> bool:
        result = await self.collection.update_one(
            {"_id": ObjectId(page_id),
             "components.component_id": component_id},
            {"$set": {"components.$": updated_component}}
        )
        logger.debug(
            f"Updated component {component_id} in page {page_id}, modified count: {result.modified_count}")
        return result.modified_count > 0


# Initialize the service with the database dependency
page_service = PageService(db)
