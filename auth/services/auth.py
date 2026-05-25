from proto import auth_pb2, auth_pb2_grpc
from utils.sms_code import sending_client, verification_client
from google.protobuf.empty_pb2 import Empty
from grpc import StatusCode
from sqlalchemy import select
from models.user import User
from utils.jwt import jwt_handler
from utils.cache import redis_client
from jwt import ExpiredSignatureError

# Overview:
# 1. SendSMSCode: SendSMSCodeRequest -> Empty
# 2. Login: LoginRequest -> AuthInfoResponse
# 3. UpdateAccessToken: UpdateAccessTokenRequest -> UpdateAccessTokenResponse


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):

    async def SendSMSCode(self, request: auth_pb2.SendSMSCodeRequest, context, session):
        tel = request.tel
        try:
            await sending_client.send_code(tel)
            return Empty()
        except Exception as e:
            print(">>>>>>>>>>验证码发送失败: ", e)
            await context.abort(code=e.status_code, details=str(e))

    async def Login(self, request: auth_pb2.LoginRequest, context, session):
        tel = request.tel
        code = request.code
        try:
            await verification_client.verify_code(tel, code)
        except Exception as e:
            print("验证码校验失败: ", e)
            await context.abort(code=e.status_code, details='Code validation failed')

        async with session.begin():
            user_result = await session.execute(select(User).where(User.tel == tel))
            user = user_result.scalar()

            if not user:
                new_user = User(tel=tel)
                session.add(new_user)
                await session.flush()
                user = new_user

            if user.is_seller:
                access_token = jwt_handler.generate_seller_access_token(user.id)
            else:
                access_token = jwt_handler.generate_access_token(user.id)

            refresh_token = jwt_handler.generate_refresh_token(user.id)

            await redis_client.set_token(user.id, refresh_token)

            response = auth_pb2.AuthInfoResponse(
                user=user.to_dict(),
                access_token=access_token,
                refresh_token=refresh_token,
            )
            return response

    async def UpdateAccessToken(
        self, request: auth_pb2.UpdateAccessTokenRequest, context, session
    ):
        user_id = request.user_id
        refresh_token = request.token
        cached_token = await redis_client.get_token(user_id)

        if refresh_token != cached_token:
            await context.abort(
                code=StatusCode.PERMISSION_DENIED,
                details="Refresh Token expired",
            )

        try:
            access_token = jwt_handler.update_access_token(refresh_token)
        except ValueError as ve:
            print("刷新Access Token失败：", str(ve))
            await context.abort(code=StatusCode.PERMISSION_DENIED, details=str(ve))
        except ExpiredSignatureError:
            await context.abort(
                code=StatusCode.PERMISSION_DENIED, details="Refresh Token expired"
            )
        except Exception as e:
            print("刷新Access Token失败：", str(e))
            await context.abort(code=StatusCode.INTERNAL, details=str(e))

        response = auth_pb2.UpdateAccessTokenResponse(token=access_token)
        return response
