from pydantic import BaseModel
from typing import List
from decimal import Decimal


class GetProductDetailResponseModel(BaseModel):
    id: str
    title: str
    price: Decimal
    covers: List[str]
    detail: str
    created_at: str


class GetProductListResponseModel(BaseModel):
    products: List[GetProductDetailResponseModel] = None


class DeleteProductResponseModel(BaseModel):
    result: str = "删除商品成功！"


class GetSeckillDetailResponseModel(BaseModel):
    id: str
    seckill_price: Decimal
    starts_at: str
    ends_at: str
    created_at: str
    stock: int
    max_per_buyer: int
    product: GetProductDetailResponseModel


class GetSeckillListResponseModel(BaseModel):
    seckills: List[GetSeckillDetailResponseModel] = None


class DeleteSeckillResponseModel(BaseModel):
    result: str = "删除秒杀成功！"


class GetOrderDetailResponseModel(BaseModel):
    id: str
    user_id: str
    quantity: int
    amount: Decimal
    status: int
    created_at: str
    seckill: GetSeckillDetailResponseModel
    address: str


class GetOrderListResponseModel(BaseModel):
    orders: List[GetOrderDetailResponseModel] = None

class GetAuthenticatedUserListResponseModel(BaseModel):
    user_ids: List[str]