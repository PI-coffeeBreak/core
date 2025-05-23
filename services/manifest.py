from dependencies.mongodb import db
from motor.motor_asyncio import AsyncIOMotorClient
from schemas.manifest import Icon, Manifest
from exceptions.manifest import ManifestNotFoundError, ManifestUpdateError, ManifestInsertIconError
from typing import Optional
from pydantic import BaseModel


class ManifestService:
    """
    Service for managing the PWA manifest.
    The manifest is stored in MongoDB and contains information about the PWA such as name, description, icons, etc.
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.manifest_collection = db['manifest']

    async def get_manifest(self) -> Manifest:
        """
        Retrieves the current PWA manifest from the database.
        
        Returns:
            Manifest: The current manifest object
            
        Raises:
            ManifestNotFoundError: If no manifest exists in the database
        """
        manifest = await self.manifest_collection.find_one({"id": "/app?source=pwa"})
        if not manifest:
            raise ManifestNotFoundError()
        return Manifest(**manifest)

    async def update_manifest(self, new_manifest: Manifest) -> Manifest:
        """
        Updates the PWA manifest in the database.
        If no manifest exists, creates a new one.
        
        Args:
            new_manifest (Manifest): The new manifest object to store
            
        Returns:
            Manifest: The updated manifest object
            
        Raises:
            ManifestUpdateError: If the update operation fails
        """
        try:
            result = await self.manifest_collection.update_one(
                {"id": new_manifest.id}, {"$set": new_manifest.model_dump()}
            )
            if result.matched_count == 0:
                # Create new manifest
                await self.manifest_collection.insert_one(new_manifest.model_dump())
            return new_manifest
        except Exception as e:
            raise ManifestUpdateError(str(e))

    async def insert_icon(self, icon: Icon) -> Icon:
        """
        Inserts a new icon into the manifest.
        If an icon with the same size and purpose already exists, it will be replaced.
        
        Args:
            icon (Icon): The icon object to insert
            
        Returns:
            Icon: The inserted icon object
            
        Raises:
            ManifestInsertIconError: If the icon insertion fails
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
