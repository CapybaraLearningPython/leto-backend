from pydantic import BaseModel


class SendSMSCodeResponseModel(BaseModel):
    result: str = "验证码发送成功，请注意查收！"


class LoginResponseModel(BaseModel):
    user: dict
    access_token: str
    refresh_token: str


class UpdateAccessTokenResponse(BaseModel):
    token: str
