from grpc_interceptor import AsyncServerInterceptor
import typing
import grpc
from grpc import StatusCode
from models import AsyncSessionFactory
from grpc_interceptor.exceptions import GrpcException
import traceback


class SeckillInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: typing.Callable,
        request_or_iterator: typing.Any,
        context: grpc.ServicerContext,
        method_name: str,
    ):
        session = AsyncSessionFactory()

        if "Health" in method_name:
            return method(request_or_iterator, context)

        if "GetSeckill" in method_name or "PostPaymentResult" in method_name:
            try:
                return await method(request_or_iterator, context, session)
            except Exception as e:
                print("GetSeckill或PostPaymentResult错误: ", e)
                traceback.print_exc()
                await context.abort(code=StatusCode.INTERNAL, details=str(e))
            finally:
                await session.close()

        user_id = int(dict(context.invocation_metadata()).get("user-id"))
        if not user_id:
            await context.abort(
                code=StatusCode.UNAUTHENTICATED,
                details="Seckill拦截器解析user_id失败！",
            )
        try:
            response = await method(request_or_iterator, context, session, user_id)
            return response
        except Exception as e:
            print("Seckill拦截器错误: ", e)
            traceback.print_exc()
            await context.abort(code=StatusCode.INTERNAL, details=str(e))
        finally:
            await session.close()
