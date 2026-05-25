from utils.stubs import AdminStub
from schemas.admin.admin_responses import *
from schemas.admin.admin_requests import *


async def get_product_list_():
    async with AdminStub() as stub:
        response = await stub.make_request("get", "product/")
        return GetProductListResponseModel(products=response)


async def get_product_detail_(id: str):
    async with AdminStub() as stub:
        response = await stub.make_request("get", f"product/{id}/")
        return GetProductDetailResponseModel(**response)


async def create_product_(data: CreateProductRequestModel):
    async with AdminStub() as stub:
        response = await stub.make_request(
            "post", "product/", data.model_dump()
        )
        return GetProductDetailResponseModel(**response)


async def update_product_(id: str, data: UpdateProductRequestModel):
    async with AdminStub() as stub:
        response = await stub.make_request(
            "patch",
            f"product/{id}/",
            data.model_dump(exclude_none=True),
            
        )
        return GetProductDetailResponseModel(**response)


async def delete_product_(id: str):
    async with AdminStub() as stub:
        await stub.make_request("delete", f"product/{id}/")
        return DeleteProductResponseModel()


async def get_seckill_list_():
    async with AdminStub() as stub:
        response = await stub.make_request("get", "seckill/")
        return GetSeckillListResponseModel(seckills=response)


async def get_seckill_detail_(id: str):
    async with AdminStub() as stub:
        response = await stub.make_request("get", f"seckill/{id}/")
        return GetSeckillDetailResponseModel(**response)


async def create_seckill_(data: CreateSeckillRequestModel):
    async with AdminStub() as stub:
        response = await stub.make_request(
            "post", "seckill/", data.model_dump()
        )
        return GetSeckillDetailResponseModel(**response)


async def update_seckill_(id: str, data: UpdateSeckillRequestModel):
    async with AdminStub() as stub:
        response = await stub.make_request(
            "patch",
            f"seckill/{id}/",
            data.model_dump(exclude_none=True),
            
        )
        return GetSeckillDetailResponseModel(**response)


async def delete_seckill_(id: str):
    async with AdminStub() as stub:
        await stub.make_request("delete", f"seckill/{id}/")
        return DeleteSeckillResponseModel()


async def get_order_list_():
    async with AdminStub() as stub:
        response = await stub.make_request("get", "order/")
        return GetOrderListResponseModel(orders=response)


async def get_order_detail_(id: str):
    async with AdminStub() as stub:
        response = await stub.make_request("get", f"order/{id}/")
        return GetOrderDetailResponseModel(**response)


async def update_order_(id: str, data: UpdateOrderRequestModel):
    async with AdminStub() as stub:
        response = await stub.make_request(
            "patch", f"order/{id}/", data.model_dump(exclude_none=True)
        )
        return GetOrderDetailResponseModel(**response)


async def get_authenticated_user_list_():
    async with AdminStub() as stub:
        response = await stub.make_request("get", "user_login_status/")
        return GetAuthenticatedUserListResponseModel(**response)


async def logout_users_(data: LogoutUsersRequestModel):
    async with AdminStub() as stub:
        response = await stub.make_request(
            "post",
            "user_login_status/",
            data.model_dump(exclude_none=True),
            
        )
        return response
