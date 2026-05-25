from pydantic import BaseModel


class CreateOrUpdateAddressRequestModel(BaseModel):
    name: str
    tel: str
    region: str
    detail: str


class UpdateAvatarRequestModel(BaseModel):
    file_name: str
    content_type: str

class UploadAvatarRequestModel(BaseModel):
    file_url: str

class GetAvatarDetailRequestModel(BaseModel):
    user_id: str
