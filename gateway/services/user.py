from utils.stubs import UserStub
from utils.decorators import grpc_error_handler
from proto import user_pb2
from typing import List
from schemas.user.user_requests import *
from schemas.user.user_responses import *
from utils.message_to_dict import convert_to_dict
from google.protobuf.empty_pb2 import Empty

# Overview:
# 1. CreateAddress: CreateAddressRequest -> AddressInfoResponse
# 2. UpdateAddress: UpdateAddressRequest -> AddressInfoResponse
# 3. GetAddressList: GetAddressListRequest -> AddressListResponse
# 4. DeleteAddress: DeleteAddressRequest -> Empty
# 5. UpdateAvatar: UpdateAvatarRequest -> UpdateAvatarResponse


@grpc_error_handler
async def create_address_(
    data: CreateOrUpdateAddressRequestModel, metadata: List[tuple]
):
    async with UserStub() as stub:
        request = user_pb2.CreateAddressRequest(**data.model_dump())
        response = convert_to_dict(
            await stub.CreateAddress(request, metadata=metadata),
        )

        return AddressInfoResponse(**response)


@grpc_error_handler
async def update_address_(
    id: int | str, data: CreateOrUpdateAddressRequestModel, metadata: List[tuple]
):
    async with UserStub() as stub:
        id = int(id)
        data_dict = data.model_dump()
        data_dict["id"] = id
        request = user_pb2.UpdateAddressRequest(**data_dict)
        response = convert_to_dict(
            await stub.UpdateAddress(request, metadata=metadata),
        )

        return AddressInfoResponse(**response)


@grpc_error_handler
async def get_address_list_(metadata: List[tuple], page: int, size: int):
    async with UserStub() as stub:
        request = user_pb2.GetAddressListRequest(page=page, size=size)
        response = convert_to_dict(
            await stub.GetAddressList(request, metadata=metadata),
        )

        return GetAddressListResponse(**response)


@grpc_error_handler
async def delete_address_(id: int | str, metadata: List[tuple]):
    async with UserStub() as stub:
        id = int(id)
        request = user_pb2.DeleteAddressRequest(id=id)
        await stub.DeleteAddress(request, metadata=metadata)

        return DeleteAddressResponseModel()


@grpc_error_handler
async def update_avatar_(data: UpdateAvatarRequestModel, metadata: List[tuple]):
    async with UserStub() as stub:
        request = user_pb2.UpdateAvatarRequest(**data.model_dump())
        response = convert_to_dict(
            await stub.UpdateAvatar(request, metadata=metadata),
        )

        return UpdateAvatarResponseModel(**response)


@grpc_error_handler
async def upload_avatar_(data: UploadAvatarRequestModel, metadata: List[tuple]):
    async with UserStub() as stub:
        request = user_pb2.UploadAvatarRequest(**data.model_dump())
        response = convert_to_dict(
            await stub.UploadAvatar(request, metadata=metadata),
        )
        return AvatarInfoResponseModel(**response)
    

@grpc_error_handler
async def get_avatar_detail_(metadata: List[tuple]):
    async with UserStub() as stub:
        request = Empty()
        response = convert_to_dict(
            await stub.GetAvatarDetail(request, metadata=metadata),
        )
        return AvatarInfoResponseModel(**response)
