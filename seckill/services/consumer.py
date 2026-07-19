from confluent_kafka import Consumer
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from models.seckill import Seckill, Order
from models import AsyncSessionFactory
import json
import asyncio
from utils.alipay import alipay_client
from utils.cache import redis_client

consumer = Consumer(
    {
        "bootstrap.servers": "127.0.0.1:9092",
        "group.id": "seckill_group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
)
consumer.subscribe(["seckill"])


class RetryableError(Exception):
    pass


class NonRetryableError(Exception):
    pass


async def create_order(request: dict):
    quantity = request["quantity"]
    seckill_id = request["seckill_id"]
    address = request["address"]
    user_id = request["user_id"]
    async with AsyncSessionFactory() as session:
        async with session.begin():
            # DB层数据校验
            seckill_result = await session.execute(
                select(Seckill)
                .where(Seckill.id == seckill_id)
                .options(selectinload(Seckill.product))
            )
            seckill = seckill_result.scalar()
            if not seckill:
                raise NonRetryableError(
                    "Consumer处理订单失败：找不到对应的秒杀信息！"
                )  # 不释放锁

            order_result = await session.execute(
                select(Order).where(
                    Order.seckill_id == seckill_id, Order.user_id == user_id
                )
            )
            order = order_result.scalar()
            if order:
                raise NonRetryableError(
                    "Consumer处理订单失败：已存在相同订单！"
                )  # 不释放锁

            if quantity <= 0 or quantity > seckill.max_per_buyer:
                raise RetryableError(
                    "Consumer处理订单失败：购买数量不正确或超过了每人限购数量！"  # 释放锁
                )

            # 通过update可以实现校验库存+扣减库存的原子操作（乐观锁）
            update_stock_result = await session.execute(
                update(Seckill)
                .where(Seckill.id == seckill_id, Seckill.stock >= quantity)
                .values(stock=Seckill.stock - quantity)
            )

            if update_stock_result.rowcount == 0:
                raise RetryableError("Consumer处理订单失败：库存不足！")  # 释放锁

            order = Order(
                quantity=quantity,
                amount=quantity * seckill.seckill_price,
                order_str="pending",
                address=address,
                seckill_id=seckill_id,
                user_id=user_id,
            )
            session.add(order)
            await session.flush()
            order_str = await alipay_client.get_order_string(
                order, seckill.product.title
            )
            order.order_str = order_str

            await redis_client.set_order_str(order_str, user_id, seckill_id)

    return "订单已创建！"


async def main():
    print(r"""
       ,--./,-.
      / o      \
     |          |
      \        /
       `._,._.' Kafka consumer now running...
""")
    loop = asyncio.get_event_loop()
    while True:
        message = await loop.run_in_executor(None, consumer.poll, 1.0)

        if message is None:
            continue

        if message.error():
            print(f"接收消息失败：{str(message.error())}")
            continue

        request = json.loads(message.value().decode("utf-8"))
        try:
            response = await create_order(request)
            consumer.commit(message)
            print(response)
        except NonRetryableError as e:
            consumer.commit(message)
            print(f"Consumer创建订单失败：{str(e)}")
        except RetryableError as e:
            consumer.commit(message)
            print(f"Consumer创建订单失败：{str(e)}")
            await redis_client.release_key(request["user_id"], request["seckill_id"])
        except Exception as e:
            print(f"Consumer创建订单失败：{str(e)}")
            await redis_client.release_key(request["user_id"], request["seckill_id"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Consumer错误：{str(e)}")
