from qdrant_client import AsyncQdrantClient

from app.core import settings


class QdrantManager:
    _client: AsyncQdrantClient | None = None

    @classmethod
    async def init(cls) -> None:
        cls._client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )

    @classmethod
    def get_client(cls) -> AsyncQdrantClient:
        if cls._client is None:
            raise RuntimeError("QdrantManager not initialised — call init() first")
        return cls._client

    @classmethod
    async def close(cls) -> None:
        if cls._client is not None:
            await cls._client.close()
            cls._client = None
