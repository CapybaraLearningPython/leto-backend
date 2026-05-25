from proto import user_pb2, user_pb2_grpc
from google.protobuf.empty_pb2 import Empty
from grpc import StatusCode
from sqlalchemy import select
from models.address import Address
from models.avatar import Avatar
from utils.oss import oss_client


class UserServicer(user_pb2_grpc.UserServiceServicer):
    async def CreateAddress(
        self, request: user_pb2.CreateAddressRequest, context, session, user_id: int
    ):
        name = request.name
        tel = request.tel
        region = request.region
        detail = request.detail
        async with session.begin():
            address = Address(
                name=name, tel=tel, region=region, detail=detail, user_id=user_id
            )
            session.add(address)
            await session.flush()
            response = user_pb2.AddressInfoResponse(**address.to_dict())
            return response

    async def UpdateAddress(
        self, request: user_pb2.UpdateAddressRequest, context, session, user_id: int
    ):
        id = request.id
        name = request.name
        tel = request.tel
        region = request.region
        detail = request.detail
        async with session.begin():
            address_result = await session.execute(
                select(Address).where(Address.id == id, Address.user_id == user_id)
            )
            address = address_result.scalar()
            if not address:
                await context.abort(
                    code=StatusCode.NOT_FOUND, details="更新地址失败：找不到该地址！"
                )
            address.name = name
            address.tel = tel
            address.region = region
            address.detail = detail
            response = user_pb2.AddressInfoResponse(**address.to_dict())
            return response

    async def GetAddressList(
        self, request: user_pb2.GetAddressListRequest, context, session, user_id: int
    ):
        page = request.page or 1
        size = request.size or 10
        offset = (page - 1) * size
        async with session.begin():
            address_results = await session.execute(
                select(Address)
                .order_by(Address.id.desc())
                .where(Address.user_id == user_id)
                .limit(size)
                .offset(offset)
            )
            address_objs = address_results.scalars().all()
            addresses = []
            for address_obj in address_objs:
                addresses.append(address_obj.to_dict())
            response = user_pb2.AddressListResponse(addresses=addresses)
            return response

    async def DeleteAddress(
        self, request: user_pb2.DeleteAddressRequest, context, session, user_id: int
    ):
        id = request.id
        async with session.begin():
            address_result = await session.execute(
                select(Address).where(Address.id == id, Address.user_id == user_id)
            )
            address = address_result.scalar()
            if not address:
                await context.abort(
                    code=StatusCode.NOT_FOUND, details="删除地址失败：找不到该地址！"
                )
            await session.delete(address)

        return Empty()

    async def UpdateAvatar(
        self, request: user_pb2.UpdateAvatarRequest, context, session, user_id: int
    ):
        file_name = request.file_name
        content_type = request.content_type
        presigned_url, signed_headers, file_url = (
            await oss_client.generate_presigned_url(
                file_name=file_name, content_type=content_type
            )
        )
        response = user_pb2.UpdateAvatarResponse(
            presigned_url=presigned_url,
            signed_headers=signed_headers,
            file_url=file_url,
        )

        return response

    async def UploadAvatar(
        self, request: user_pb2.UploadAvatarRequest, context, session, user_id
    ):
        file_url = request.file_url
        async with session.begin():
            avatar_result = await session.execute(
                select(Avatar).where(Avatar.user_id == user_id)
            )
            avatar = avatar_result.scalar()
            if not avatar:
                avatar = Avatar(url=file_url, user_id=user_id)
                session.add(avatar)
                await session.flush()
            avatar.url = file_url
            
            response = user_pb2.AvatarInfoResponse(**avatar.to_dict())
            return response

    async def GetAvatarDetail(self, request: Empty, context, session, user_id):
        async with session.begin():
            avatar_result = await session.execute(
                select(Avatar).where(Avatar.user_id == user_id)
            )
            avatar = avatar_result.scalar()
            response = user_pb2.AvatarInfoResponse(**avatar.to_dict())
            return response
