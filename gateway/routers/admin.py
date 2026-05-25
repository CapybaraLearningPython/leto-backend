from fastapi import APIRouter, Depends
from schemas.admin.admin_requests import *
from services.admin import *
from utils.jwt import jwt_handler
from typing import Annotated

router = APIRouter(prefix="/admin", tags=["admin"])
auth_dep = jwt_handler.is_seller_dependency


# Product
@router.get("/product")
async def get_product_list(user_id: Annotated[int, Depends(auth_dep)]):
    return await get_product_list_()


@router.get("/product/{id}")
async def get_product_detail(id: str, user_id: Annotated[int, Depends(auth_dep)]):
    return await get_product_detail_(id)


@router.post("/product")
async def create_product(
    data: CreateProductRequestModel, user_id: Annotated[int, Depends(auth_dep)]
):
    return await create_product_(data)


@router.patch("/product/{id}")
async def update_product(
    id: str, data: UpdateProductRequestModel, user_id: Annotated[int, Depends(auth_dep)]
):
    return await update_product_(id, data)


@router.delete("/product/{id}")
async def delete_product(id: str, user_id: Annotated[int, Depends(auth_dep)]):
    return await delete_product_(id)


# Seckill
@router.get("/seckill")
async def get_seckill_list(user_id: Annotated[int, Depends(auth_dep)]):
    return await get_seckill_list_()


@router.get("/seckill/{id}")
async def get_seckill_detail(id: str, user_id: Annotated[int, Depends(auth_dep)]):
    return await get_seckill_detail_(id)


@router.post("/seckill")
async def create_seckill(
    data: CreateSeckillRequestModel, user_id: Annotated[int, Depends(auth_dep)]
):
    return await create_seckill_(data)


@router.patch("/seckill/{id}")
async def update_seckill(
    id: str, data: UpdateSeckillRequestModel, user_id: Annotated[int, Depends(auth_dep)]
):
    return await update_seckill_(id, data)


@router.delete("/seckill/{id}")
async def delete_seckill(id: str, user_id: Annotated[int, Depends(auth_dep)]):
    return await delete_seckill_(id)


# Order
@router.get("/order")
async def get_order_list(user_id: Annotated[int, Depends(auth_dep)]):
    return await get_order_list_()


@router.get("/order/{id}")
async def get_order_detail(id: str, user_id: Annotated[int, Depends(auth_dep)]):
    return await get_order_detail_(id)


@router.patch("/order/{id}")
async def update_order(
    id: str, data: UpdateOrderRequestModel, user_id: Annotated[int, Depends(auth_dep)]
):
    return await update_order_(id, data)


# User
@router.get("/users")
async def get_authenticated_user_list(user_id: Annotated[int, Depends(auth_dep)]):
    return await get_authenticated_user_list_()


@router.post("/users")
async def logout_users(
    data: LogoutUsersRequestModel, user_id: Annotated[int, Depends(auth_dep)]
):
    return await logout_users_(data)
