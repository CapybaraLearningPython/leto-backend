from pydantic import BaseModel

class LoginRequestModel(BaseModel):
    tel: str
    code: str

class UpdateAccessTokenRequest(BaseModel):
    refresh_token: str
    user_id: str