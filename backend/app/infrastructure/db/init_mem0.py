from mem0 import MemoryClient

from app.core import settings


class Mem0Manager:
    _client = None

    @classmethod
    async def init(cls):
        cls._client = MemoryClient(api_key=settings.mem0_api_key)

    @classmethod
    async def get_client(cls) -> MemoryClient:
        return cls._client