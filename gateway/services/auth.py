from utils.stubs import AuthStub
from typing import List
from utils.decorators import grpc_error_handler
from proto import auth_pb2
from schemas.auth.auth_requests import *
from schemas.auth.auth_responses import *
from utils.message_to_dict import convert_to_dict

# Overview:
# 1. SendSMSCode: SendSMSCodeRequest -> Empty
# 2. Login: LoginRequest -> AuthInfoResponse
# 3. UpdateAccessToken: UpdateAccessTokenRequest -> UpdateAccessTokenResponse


@grpc_error_handler
async def send_sms_code_(tel: str):
    async with AuthStub() as stub:
        request = auth_pb2.SendSMSCodeRequest(tel=tel)
        await stub.SendSMSCode(request=request)

        return SendSMSCodeResponseModel()


@grpc_error_handler
async def login_(data: LoginRequestModel):
    async with AuthStub() as stub:
        request = auth_pb2.LoginRequest(**data.model_dump())
        response = convert_to_dict(await stub.Login(request))

        return LoginResponseModel(**response)


@grpc_error_handler
async def update_access_token_(data: UpdateAccessTokenRequest, user_id: int):
    async with AuthStub() as stub:
        request = auth_pb2.UpdateAccessTokenRequest(
            token=data.refresh_token, user_id=user_id
        )
        response = convert_to_dict(await stub.UpdateAccessToken(request))

        return UpdateAccessTokenResponse(**response)
