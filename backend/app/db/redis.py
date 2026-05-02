import redis.asyncio as aioredis
from app.config import settings

redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20
)

def get_redis_client():
    return aioredis.Redis(connection_pool=redis_pool)
