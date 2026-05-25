from pydantic import BaseModel
from typing import List, Dict


class AddressInfoResponse(BaseModel):
    name: str
    tel: str
    region: str
    detail: str
    id: str


class GetAddressListResponse(BaseModel):
    addresses: List[AddressInfoResponse] = None


class DeleteAddressResponseModel(BaseModel):
    result: str = "地址删除成功！"


class UpdateAvatarResponseModel(BaseModel):
    presigned_url: str
    file_url: str
    signed_headers: Dict[str, str]

class AvatarInfoResponseModel(BaseModel):
    url: str
    user_id: str
    id: str