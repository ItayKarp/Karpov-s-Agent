from pymongo import MongoClient
from pymongo.server_api import ServerApi
from app.core import settings
from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:
    _client: AsyncIOMotorClient = None

    @classmethod
    async def init(cls):
        cls._client = AsyncIOMotorClient(settings.mongodb_uri)

    @classmethod
    async def close(cls):
        cls._client.close()

    @classmethod
    def get_db(cls):
        return cls._client["AIChatBots"]