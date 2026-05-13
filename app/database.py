from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_db() -> AsyncIOMotorDatabase:
    return _client[settings.MONGO_DB_NAME]


async def connect():
    global _client
    _client = AsyncIOMotorClient(settings.MONGO_URI)


async def disconnect():
    global _client
    if _client:
        _client.close()
        _client = None
