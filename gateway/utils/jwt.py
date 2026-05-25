import jwt
import settings
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from fastapi import Depends
from jwt import ExpiredSignatureError

security = HTTPBearer()


class JWTHandler:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY

    def decode_access_token(self, access_token):
        result = jwt.decode(access_token, self.secret_key, algorithms=["HS256"])
        user_id = result.get("user_id")
        token_type = result.get("token_type")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="JWT鉴权失败：无法解析user_id！",
            )

        if not token_type or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JWT鉴权失败：无法解析token_type或token_type不正确！",
            )

        return user_id

    def auth_dependency(
        self, auth_data: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ):
        try:
            user_id = str(self.decode_access_token(auth_data.credentials))
            metadata = [("user-id", user_id)]
            return metadata
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Access Token expired"
            )

    def is_seller_dependency(
        self, auth_data: Annotated[HTTPAuthorizationCredentials, Depends(security)]
    ):
        try:
            result = jwt.decode(
                auth_data.credentials, self.secret_key, algorithms=["HS256"]
            )
            user_id = result.get("user_id")
            token_type = result.get("token_type")
            is_seller = result.get("is_seller")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="JWT鉴权失败：无法解析user_id！",
                )

            if not token_type or token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="JWT鉴权失败：无法解析token_type或token_type不正确！",
                )

            if not is_seller:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="JWT鉴权失败：非商家用户无访问权限！",
                )

            return user_id
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Access Token expired"
            )


jwt_handler = JWTHandler()
auth_dep = jwt_handler.auth_dependency
