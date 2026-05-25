from fastapi import APIRouter, Depends, Form, Request
from services.seckill import *
from typing import Annotated, List
from utils.jwt import auth_dep
import json

router = APIRouter(prefix="/seckill")

# Overview:
# 1. GetSeckillDetail: GetSeckillDetailRequest -> GetSeckillDetailResponse
# 2. GetSeckillList: GetSeckillListRequest -> GetSeckillListResponse
# 3. GetOrderList: GetOrderListRequest -> GetOrderListResponse
# 4. CreateOrder: CreateOrderRequest -> CreateOrderResponse
# 5. MakePayment: MakePaymentRequest -> MakePaymentResponse
# 6. PostPaymentResult: PostPaymentResultRequest -> PostPaymentResultResponse


@router.get("/seckill_detail/{id}")
async def get_seckill_detail(
    id: int | str
):
    return await get_seckill_detail_(id=id)


@router.get("/seckill_list")
async def get_seckill_list(
    page: int = 1, size: int = 10
):
    return await get_seckill_list_(page=page, size=size)


@router.get("/order_list")
async def get_order_list(
    metadata: Annotated[List[tuple], Depends(auth_dep)], page: int = 1, size: int = 10
):
    return await get_order_list_(metadata=metadata, page=page, size=size)


@router.post("/create_order")
async def create_order(
    data: CreateOrderRequestModel, metadata: Annotated[List[tuple], Depends(auth_dep)]
):
    return await create_order_(data=data, metadata=metadata)


@router.get("/make_payment/{id}")
async def make_payment(
    id: int | str, metadata: Annotated[List[tuple], Depends(auth_dep)]
):
    return await make_payment_(id=id, metadata=metadata)


@router.post("/post_payment_result")
async def post_payment_result(request: Request):
    return await post_payment_result_(request)
