from .single import SingletonMeta
from redis.asyncio import Redis
import settings


class LetoRedis(metaclass=SingletonMeta):
    def __init__(self):
        self.client = Redis(host="localhost", port=6379, db=0, decode_responses=True)
        self.key = "refresh_token_{}"

    async def set_token(self, user_id, token):
        key = self.key.format(user_id)
        await self.client.set(key, token, settings.JWT_REFRESH_TOKEN_EXPIRES)

    async def get_token(self, user_id):
        key = self.key.format(user_id)
        token = await self.client.get(key)
        return token

    async def delete_token(self, user_id):
        key = self.key.format(user_id)
        await self.client.delete(key)

redis_client = LetoRedis()