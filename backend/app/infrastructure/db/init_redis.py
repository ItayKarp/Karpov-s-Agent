from app.core import settings
from redis.asyncio import Redis

class RedisManager:
    _client: Redis = None

    @classmethod
    async def init(cls):
        cls._client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            username=settings.redis_user,
            password=settings.redis_pass,
            decode_responses=True
        )

    @classmethod
    async def close(cls):
        await cls._client.aclose()

    @classmethod
    def get_client(cls) -> Redis:
        return cls._client