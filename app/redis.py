import redis.asyncio as redis
from .config import settings

async def get_redis_connection():
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()