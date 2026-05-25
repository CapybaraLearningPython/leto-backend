from proto import user_pb2, user_pb2_grpc
import grpc
import asyncio


async def test_create_addresss(stub):
    metadata = [("user-id", "2053776674599731200")]
    name = "Eric"
    tel = "18899996666"
    region = "成都"
    detail = "锦江区"
    request = user_pb2.CreateAddressRequest(
        name=name, tel=tel, region=region, detail=detail
    )
    response = await stub.CreateAddress(request, metadata=metadata)
    print(response)


async def test_update_address(stub):
    metadata = [("user-id", "2053776674599731200")]
    name = "Eric"
    tel = "18899998888"
    region = "成都"
    detail = "锦江区"
    id = 2053834812283682816
    request = user_pb2.UpdateAddressRequest(
        name=name, tel=tel, region=region, detail=detail, id=id
    )
    response = await stub.UpdateAddress(request, metadata=metadata)
    print(response)

async def test_get_address_list(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = user_pb2.GetAddressListRequest()
    response = await stub.GetAddressList(request, metadata=metadata)
    print(response)

async def test_delete_address(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = user_pb2.DeleteAddressRequest(id=2053834812283682816)
    response = await stub.DeleteAddress(request, metadata=metadata)
    print(response)

async def test_update_avatar(stub):
    metadata = [("user-id", "2053776674599731200")]
    request = user_pb2.UpdateAvatarRequest(
        file_name="my_avatar.jpg",
        content_type="image/jpg"
    )
    response = await stub.UpdateAvatar(request, metadata=metadata)
    print(response)

async def main():
    async with grpc.aio.insecure_channel("127.0.0.1:8002") as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        # await test_create_addresss(stub)
        # await test_update_address(stub)
        # await test_get_address_list(stub)
        # await test_delete_address(stub)
        await test_update_avatar(stub)


if __name__ == "__main__":
    asyncio.run(main())
