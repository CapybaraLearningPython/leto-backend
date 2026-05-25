from models import AsyncSessionFactory
from models.seckill import Product, Seckill
from datetime import datetime, timedelta
from utils.cache import redis_client
import asyncio


async def main():
    async with AsyncSessionFactory() as session:
        async with session.begin():
            product = Product(
                title="iPhone 16 Pro 256G",
                price=7999.00,
                covers=[
                    "https://example.com/iphone-cover-1.jpg",
                    "https://example.com/iphone-cover-2.jpg",
                ],
                detail="Apple A18 Pro 芯片，钛金属边框，支持 Apple Intelligence。",
            )

            seckill = Seckill(
                seckill_price=5999.00,
                starts_at=datetime.now(),
                ends_at=datetime.now() + timedelta(days=365),
                stock=20,
                max_per_buyer=1,
                product=product,
            )

            session.add(product)
            session.add(seckill)
            await session.flush()
            await redis_client.add_seckill(seckill)
            await redis_client.init_stock(seckill_id=seckill.id, stock=seckill.stock)


if __name__ == "__main__":
    asyncio.run(main())
