from pydantic import BaseModel, Field


class CreateOrderRequestModel(BaseModel):
    quantity: int
    seckill_id: int
    address: str = Field(min_length=5)


class PostPaymentResultRequestModel(BaseModel):
    result: str
