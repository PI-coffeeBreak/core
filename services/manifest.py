from dependencies.mongodb import db
from motor.motor_asyncio import AsyncIOMotorClient
from schemas.manifest import Icon, Manifest
from exceptions.manifest import ManifestNotFoundError, ManifestUpdateError, ManifestInsertIconError
from typing import Optional
from pydantic import BaseModel


class ManifestService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.manifest_collection = db['manifest']

    async def get_manifest(self) -> Manifest:
        manifest = await self.manifest_collection.find_one({"name": "coffeeBreak"})
        if not manifest:
            raise ManifestNotFoundError()
        return Manifest(**manifest)

    async def update_manifest(self, new_manifest: Manifest) -> Manifest:
        try:
            result = await self.manifest_collection.update_one(
                {"name": new_manifest.name}, {"$set": new_manifest.model_dump()}
            )
            if result.matched_count == 0:
                # Create new manifest
                await self.manifest_collection.insert_one(new_manifest.model_dump())
            return new_manifest
        except Exception as e:
            raise ManifestUpdateError(str(e))

    async def insert_icon(self, icon: Icon) -> Icon:
        """
        Insert a new icon into the manifest.
        Replace if there is already an icon with the same size.
        """
        try:
            manifest = await self.get_manifest()

            icons = [i for i in manifest.icons if i.sizes != icon.sizes or i.purpose != icon.purpose]
            icons.append(icon)
            manifest.icons = icons

            await self.update_manifest(manifest)
            return icon
        except Exception as e:
            raise ManifestInsertIconError(str(e))
