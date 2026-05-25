from proto import seckill_pb2, seckill_pb2_grpc
import grpc
import asyncio


async def test_create_order(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = seckill_pb2.CreateOrderRequest(
        quantity=1, seckill_id=2054879978264199168, address="成都市"
    )
    response = await stub.CreateOrder(request, metadata=metadata)
    print(response)


async def test_get_seckill_detail(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = seckill_pb2.GetSeckillDetailRequest(id=2054796462818066432)
    response = await stub.GetSeckillDetail(request, metadata=metadata)
    print(response)


async def test_get_seckill_list(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = seckill_pb2.GetSeckillListRequest()
    response = await stub.GetSeckillList(request, metadata=metadata)
    print(response)


async def test_get_order_list(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = seckill_pb2.GetOrderListRequest()
    response = await stub.GetOrderList(request, metadata=metadata)
    print(response)


async def test_make_payment(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = seckill_pb2.MakePaymentRequest(id=2054879978264199168)
    response = await stub.MakePayment(request, metadata=metadata)
    print(response)

# 待测试
async def test_post_payment_result(stub):
    pass


async def main():
    async with grpc.aio.insecure_channel("127.0.0.1:8003") as channel:
        stub = seckill_pb2_grpc.SeckillServiceStub(channel)
        # await test_create_order(stub)
        # await test_get_order_list(stub)
        # await test_get_seckill_detail(stub)
        # await test_get_seckill_list(stub)
        await test_make_payment(stub)


if __name__ == "__main__":
    asyncio.run(main())
