from schemas.favicon import Favicon
from dependencies.mongodb import db

class FaviconService:
    _instance = None
    _collection_name = "favicon"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaviconService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.collection = db[self._collection_name]
            self.initialized = True

    async def store_favicon(self, favicon: Favicon) -> None:
        """
        Store the favicon URL in the database
        """
        await self.collection.update_one(
            {"_id": "current"},
            {"$set": {"url": favicon.url}},
            upsert=True
        )

    async def get_favicon(self) -> Favicon:
        """
        Retrieve the current favicon URL from the database
        """
        result = await self.collection.find_one({"_id": "current"})
        if result:
            return Favicon(url=result["url"])
        return Favicon(url="")  # Return empty favicon if none exists



