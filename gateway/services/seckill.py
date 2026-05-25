from utils.stubs import SeckillStub
from utils.decorators import grpc_error_handler
from proto import seckill_pb2
from typing import List
from schemas.seckill.seckill_requests import *
from schemas.seckill.seckill_responses import *
from utils.message_to_dict import convert_to_dict
from utils.decorators import grpc_error_handler
from fastapi import Request
import json

# Overview:
# 1. GetSeckillDetail: GetSeckillDetailRequest -> GetSeckillDetailResponse
# 2. GetSeckillList: GetSeckillListRequest -> GetSeckillListResponse
# 3. GetOrderList: GetOrderListRequest -> GetOrderListResponse
# 4. CreateOrder: CreateOrderRequest -> CreateOrderResponse
# 5. MakePayment: MakePaymentRequest -> MakePaymentResponse
# 6. PostPaymentResult: PostPaymentResultRequest -> PostPaymentResultResponse


@grpc_error_handler
async def get_seckill_detail_(id: int | str, metadata: List[tuple] = None):
    async with SeckillStub() as stub:
        id = int(id)
        request = seckill_pb2.GetSeckillDetailRequest(id=id)
        response = convert_to_dict(
            await stub.GetSeckillDetail(request, metadata=metadata),
        )
        seckill_dict = response["seckill"]

        return GetSeckillDetailResponseModel(**seckill_dict)


@grpc_error_handler
async def get_seckill_list_(page: int, size: int, metadata: List[tuple] = None):
    async with SeckillStub() as stub:
        request = seckill_pb2.GetSeckillListRequest(page=page, size=size)
        response = convert_to_dict(
            await stub.GetSeckillList(request, metadata=metadata),
        )

        return GetSeckillListResponseModel(**response)


@grpc_error_handler
async def get_order_list_(metadata: List[tuple], page: int, size: int):
    async with SeckillStub() as stub:
        request = seckill_pb2.GetOrderListRequest(page=page, size=size)
        response = convert_to_dict(
            await stub.GetOrderList(request, metadata=metadata),
        )

        return GetOrderListResponseModel(**response)


@grpc_error_handler
async def create_order_(data: CreateOrderRequestModel, metadata: List[tuple]):
    async with SeckillStub() as stub:
        request = seckill_pb2.CreateOrderRequest(**data.model_dump())
        response = convert_to_dict(
            await stub.CreateOrder(request, metadata=metadata),
        )

        return CreateOrderResponseModel(**response)


@grpc_error_handler
async def make_payment_(id: int | str, metadata: List[tuple]):
    async with SeckillStub() as stub:
        id = int(id)
        request = seckill_pb2.MakePaymentRequest(id=id)
        response = convert_to_dict(await stub.MakePayment(request, metadata=metadata))

        return MakePaymentResponseModel(**response)


@grpc_error_handler
async def post_payment_result_(request_: Request):
    async with SeckillStub() as stub:
        request = seckill_pb2.PostPaymentResultRequest(
            result=json.dumps(dict(await request_.form()))
        )
        response = convert_to_dict(await stub.PostPaymentResult(request))

        return PostPaymentResultResponseModel(**response)
