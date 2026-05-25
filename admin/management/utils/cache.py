from .single import SingletonMeta
from redis import Redis
from ..serializers import SeckillSerializer
import json
from datetime import datetime


class LetoRedis(metaclass=SingletonMeta):
    SECKILL_KEY = "seckill_{}"
    SECKILL_STOCK_KEY = "seckill_stock_{}"

    def __init__(self):
        self.client = Redis(host="localhost", port=6379, db=0, decode_responses=True)

    def _set_stock(self, seckill_serializer: SeckillSerializer, ex):
        seckill_dict = seckill_serializer.data
        key = self.SECKILL_STOCK_KEY.format(seckill_dict["id"])
        self.client.set(key, seckill_dict["stock"], ex)

    def set_seckill_cache(self, seckill_serializer: SeckillSerializer):
        seckill = seckill_serializer.save()
        key = self.SECKILL_KEY.format(seckill.id)
        ex = int((seckill.ends_at - datetime.now()).total_seconds())
        if ex > 0:
            self.client.set(key, json.dumps(SeckillSerializer(seckill).data), ex)
            self._set_stock(seckill_serializer, ex)
        else:
            self.client.delete(key)

    def delete_seckill_cache(self, seckill_serializer: SeckillSerializer):
        seckill_id = seckill_serializer.data.get("id")
        seckill_key = self.SECKILL_KEY.format(seckill_id)
        stock_key = self.SECKILL_STOCK_KEY.format(seckill_id)
        self.client.delete(seckill_key)
        self.client.delete(stock_key)

redis_client = LetoRedis()