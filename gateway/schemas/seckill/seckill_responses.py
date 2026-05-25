from pydantic import BaseModel
from typing import List
from decimal import Decimal


class ProductModel(BaseModel):
    id: str
    title: str
    price: Decimal
    covers: str
    detail: str
    created_at: str


class GetSeckillDetailResponseModel(BaseModel):
    id: str
    seckill_price: Decimal
    starts_at: str
    ends_at: str
    created_at: str
    stock: int
    max_per_buyer: int
    product: ProductModel


class GetSeckillListResponseModel(BaseModel):
    seckills: List[GetSeckillDetailResponseModel] = None


class Order(BaseModel):
    id: str
    quantity: int
    amount: Decimal
    status: int
    created_at: str
    seckill: GetSeckillDetailResponseModel
    address: str


class GetOrderListResponseModel(BaseModel):
    orders: List[Order] = None


class CreateOrderResponseModel(BaseModel):
    status: str


class MakePaymentResponseModel(BaseModel):
    order_str: str


class PostPaymentResultResponseModel(BaseModel):
    client_response: str