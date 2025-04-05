from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
logger = logging.getLogger("coffeebreak.core")

CONNECTION_STRING = os.getenv('MONGODB_URI')

db = None

if CONNECTION_STRING is None:
    logger.error("MONGODB_URI environment variable is not set.")
    raise RuntimeError("Missing MONGODB_URI environment variable")

client = AsyncIOMotorClient(CONNECTION_STRING)
db = client.get_default_database()