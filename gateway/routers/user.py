from fastapi import APIRouter, Depends
from services.user import *
from typing import Annotated, List
from utils.jwt import auth_dep

# Overview:
# 1. CreateAddress: CreateAddressRequest -> AddressInfoResponse
# 2. UpdateAddress: UpdateAddressRequest -> AddressInfoResponse
# 3. GetAddressList: GetAddressListRequest -> AddressListResponse
# 4. DeleteAddress: DeleteAddressRequest -> Empty
# 5. UpdateAvatar: UpdateAvatarRequest -> UpdateAvatarResponse

router = APIRouter(prefix="/user")


@router.post("/create_address")
async def create_address(
    data: CreateOrUpdateAddressRequestModel,
    metadata: Annotated[List[tuple], Depends(auth_dep)],
):
    return await create_address_(data=data, metadata=metadata)


@router.put("/update_address/{id}")
async def update_address(
    id: int | str,
    data: CreateOrUpdateAddressRequestModel,
    metadata: Annotated[List[tuple], Depends(auth_dep)],
):
    return await update_address_(id=id, data=data, metadata=metadata)


@router.get("/address_list")
async def get_address_list(
    metadata: Annotated[List[tuple], Depends(auth_dep)], page: int = 1, size: int = 10
):
    return await get_address_list_(metadata=metadata, page=page, size=size)


@router.delete("/delete_address/{id}")
async def delete_address(
    id: int | str, metadata: Annotated[List[tuple], Depends(auth_dep)]
):
    return await delete_address_(id=id, metadata=metadata)


@router.put("/update_avatar")
async def update_avatar(
    data: UpdateAvatarRequestModel, metadata: Annotated[List[tuple], Depends(auth_dep)]
):
    return await update_avatar_(data=data, metadata=metadata)


@router.post("/upload_avatar")
async def upload_avatar(
    data: UploadAvatarRequestModel, metadata: Annotated[List[tuple], Depends(auth_dep)]
):
    return await upload_avatar_(data=data, metadata=metadata)


@router.get("/get_avatar_detail")
async def upload_avatar(
    metadata: Annotated[List[tuple], Depends(auth_dep)]
):
    return await get_avatar_detail_(metadata=metadata)