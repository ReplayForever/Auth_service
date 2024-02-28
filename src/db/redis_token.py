from redis.asyncio import Redis

from services.abstract import AbstractStorage


class RedisToken(AbstractStorage):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def set_data(self, token: str, user_id: str):
        await self._redis.set(name=user_id, value=token, ex=10)
