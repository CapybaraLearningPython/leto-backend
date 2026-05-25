from pydantic import BaseModel
from typing import List


class CreateProductRequestModel(BaseModel):
    title: str
    price: str
    covers: List[str]
    detail: str


class UpdateProductRequestModel(BaseModel):
    title: str = None
    price: str = None
    covers: List[str] = None
    detail: str = None


class CreateSeckillRequestModel(BaseModel):
    seckill_price: str
    starts_at: str
    ends_at: str
    stock: int
    max_per_buyer: int
    product_id: int


class UpdateSeckillRequestModel(BaseModel):
    seckill_price: str = None
    starts_at: str = None
    ends_at: str = None
    stock: int = None
    max_per_buyer: int = None
    product_id: int = None


class UpdateOrderRequestModel(BaseModel):
    address: str = None


class LogoutUsersRequestModel(BaseModel):
    user_ids: List[str]
