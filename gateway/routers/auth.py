from fastapi import APIRouter
from services.auth import *

router = APIRouter(prefix="/auth")

# Overview:
# 1. SendSMSCode: SendSMSCodeRequest -> Empty
# 2. Login: LoginRequest -> AuthInfoResponse
# 3. UpdateAccessToken: UpdateAccessTokenRequest -> UpdateAccessTokenResponse


@router.get("/send_code/{tel}")
async def send_sms_code(tel):
    return await send_sms_code_(tel)


@router.post("/login")
async def log_in(data: LoginRequestModel):
    return await login_(data)


@router.post("/update_access_token/{user_id}")
async def update_access_token(
    data: UpdateAccessTokenRequest, user_id: int
):

    return await update_access_token_(data, user_id)