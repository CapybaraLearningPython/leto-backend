from .single import SingletonMeta
import redis.asyncio as redis
from models.seckill import Seckill
from models.seckill import Order
import json
from datetime import datetime


class LetoRedis(metaclass=SingletonMeta):

    SECKILL_KEY = "seckill_{}"
    SECKILL_ORDER_KEY = "seckill_order_{user_id}_{seckill_id}"
    SECKILL_STOCK_KEY = "seckill_stock_{}"
    SECKILL_ORDER_LOCK_KEY = "order_lock_{user_id}_{seckill_id}"
    SECKILL_ORDER_STR_KEY = "seckill_order_str_{user_id}_{seckill_id}"

    def __init__(self):
        self.client = redis.Redis(host="localhost", port=6379, db=0)

    async def set(self, key, value, ex=5 * 60 * 60):
        await self.client.set(key, value, ex)

    async def set_dict(self, key: str, value: dict, ex: int = 5 * 60 * 60):
        await self.set(key, json.dumps(value), ex)

    async def get(self, key):
        value = await self.client.get(key)
        if type(value) == bytes:
            return value.decode("utf-8")
        return value

    async def get_dict(self, key: str):
        value = await self.get(key)
        if not value:
            return None
        return json.loads(value)

    async def delete(self, key):
        await self.client.delete(key)

    async def add_seckill(self, seckill: Seckill):
        seckill_dict = seckill.to_dict()
        key = self.SECKILL_KEY.format(seckill.id)
        ex = int((seckill.ends_at - datetime.now()).total_seconds())
        await self.set_dict(key, seckill_dict, ex=ex)

    async def get_seckill(self, seckill_id: int):
        key = self.SECKILL_KEY.format(seckill_id)
        seckill_dict = await self.get_dict(key)
        return seckill_dict

    async def init_stock(self, seckill_id: int, stock: int):
        key = self.SECKILL_STOCK_KEY.format(seckill_id)
        await self.set(key, stock)

    async def get_stock(self, seckill_id: int):
        key = self.SECKILL_STOCK_KEY.format(seckill_id)
        return await self.get(key)

    async def decrease_stock(self, seckill: dict, quantity: int, user_id: int):
        lock_key = self.SECKILL_ORDER_LOCK_KEY.format(
            user_id=user_id, seckill_id=seckill["id"]
        )
        stock_key = self.SECKILL_STOCK_KEY.format(seckill["id"])

        # 原子扣减库存并防止重复下单
        lua = """
            local lock_key = KEYS[1]
            local stock_key = KEYS[2]
            local quantity = tonumber(ARGV[1])
            local ttl = tonumber(ARGV[2])
            local max_quantity = tonumber(ARGV[3])

            -- 防止重复下单
            if redis.call('exists', lock_key) == 1 then
                return -4
            end

            -- 检查限购和库存
            if quantity <= 0 or quantity > max_quantity then
                return -1
            end

            local stock = redis.call('get', stock_key)
            if not stock then
                return -3
            end

            stock = tonumber(stock)
            if not stock then
                return -3
            end

            if stock < quantity then
                return -2
            end
            
            -- 扣减库存并返回剩余库存
            local remain = redis.call('decrby', stock_key, quantity)
            redis.call('set', lock_key, 1, 'EX', ttl, 'NX')
            return remain
        """

        ttl = int(
            (
                datetime.fromisoformat(seckill["ends_at"]) - datetime.now()
            ).total_seconds()
        )
        if ttl <= 0:
            return -5

        try:
            result = await self.client.eval(
                lua, 2, lock_key, stock_key, quantity, ttl, seckill["max_per_buyer"]
            )
        except Exception as e:
            return -6

        return result

    async def release_key(self, user_id: int, seckill_id: int):
        key = self.SECKILL_ORDER_LOCK_KEY.format(user_id=user_id, seckill_id=seckill_id)
        self.client.delete(key)

    async def rollback(self, seckill_id: int, quantity: int, user_id: int):
        lua = """
            local stock_key = KEYS[1]
            local lock_key = KEYS[2]
            local quantity = tonumber(ARGV[1])

            redis.call('incrby', stock_key, quantity)
            redis.call('del', lock_key)
        """

        stock_key = self.SECKILL_STOCK_KEY.format(seckill_id)
        lock_key = self.SECKILL_ORDER_LOCK_KEY.format(
            user_id=user_id, seckill_id=seckill_id
        )
        await self.client.eval(lua, 2, stock_key, lock_key, quantity)
        return 1

    async def set_order_str(self, order_str: str, user_id: int, seckill_id: int):
        key = self.SECKILL_ORDER_STR_KEY.format(user_id=user_id, seckill_id=seckill_id)
        await self.client.set(name=key, value=order_str, ex=900)

    async def get_order_str(self, user_id: int, seckill_id: int):
        key = self.SECKILL_ORDER_STR_KEY.format(user_id=user_id, seckill_id=seckill_id)
        print("key", key)
        order_str = await self.get(key)
        return order_str


redis_client = LetoRedis()
