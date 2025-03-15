from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
logger = logging.getLogger("coffeebreak.core")

CONNECTION_STRING = os.getenv('MONGODB_URI')

if CONNECTION_STRING is not None:
    client = AsyncIOMotorClient(CONNECTION_STRING)

    db = client.get_default_database()