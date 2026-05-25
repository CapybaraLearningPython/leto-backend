import jwt
from datetime import datetime
import settings
from jwt import ExpiredSignatureError


class JWTHandler():
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY

    def generate_access_token(self, user_id: int):
        access_payload = dict(user_id=user_id)
        access_payload["exp"] = int(
            (datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES).timestamp()
        )
        access_payload["token_type"] = "access"
        access_token = jwt.encode(access_payload, self.secret_key, algorithm="HS256")

        return access_token
    
    def generate_seller_access_token(self, user_id:int):
        access_payload = dict(user_id=user_id, is_seller=True)
        access_payload["exp"] = int(
            (datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES).timestamp()
        )
        access_payload["token_type"] = "access"
        access_token = jwt.encode(access_payload, self.secret_key, algorithm="HS256")

        return access_token

    def generate_refresh_token(self, user_id: int):
        refresh_payload = dict(user_id=user_id)
        refresh_payload["exp"] = int(
            (datetime.now() + settings.JWT_REFRESH_TOKEN_EXPIRES).timestamp()
        )
        refresh_payload["token_type"] = "refresh"
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm="HS256")

        return refresh_token

    def update_access_token(self, refresh_token: str):
        try:
            payload = jwt.decode(
                refresh_token,
                self.secret_key,
                algorithms=["HS256"],
            )
        except ExpiredSignatureError:
            raise
        
        token_type = payload.get("token_type")
        if not token_type or token_type != "refresh":
            raise ValueError("Token类型错误或不存在！")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("无法解析user_id！")

        access_token = self.generate_access_token(user_id)

        return access_token


jwt_handler = JWTHandler()
