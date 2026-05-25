from proto import auth_pb2, auth_pb2_grpc
import grpc
from services import auth
import asyncio


async def test_SendSMS_code(stub):
    tel = "18580558352"
    request = auth_pb2.SendSMSCodeRequest(tel=tel)
    response = await stub.SendSMSCode(request)
    print(response)


async def test_login(stub, code):
    tel = "18580558352"
    request = auth_pb2.LoginRequest(tel=tel, code=code, is_seller=True)
    response = await stub.Login(request)
    print(response)


async def test_update_access_token(stub, refresh_token):
    metadata = [("user-id", "2053776674599731200")]
    request = auth_pb2.UpdateAccessTokenRequest(token=refresh_token)
    response = await stub.UpdateAccessToken(request, metadata=metadata)
    print(response)


async def main():
    async with grpc.aio.insecure_channel("127.0.0.1:8001") as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        # await test_SendSMS_code(stub)
        # await test_login(stub, "1739")
        # await test_update_access_token(
        #     stub,
        #     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyMDUzNzc2Njc0NTk5NzMxMjAwLCJleHAiOjE3NzkwOTg4ODYsInRva2VuX3R5cGUiOiJyZWZyZXNoIn0.KWQWOhKR_HJxc1PspGSJlYmLAlUuUgPrgODY9Ehz_wg",
        # )


if __name__ == "__main__":
    asyncio.run(main())
