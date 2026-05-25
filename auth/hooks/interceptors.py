from grpc_interceptor import AsyncServerInterceptor
import typing
from grpc import StatusCode
from models import AsyncSessionFactory
import grpc


class AuthInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: typing.Callable,
        request_or_iterator: typing.Any,
        context: grpc.ServicerContext,
        method_name: str,
    ):
        if "Health" in method_name:
            return method(request_or_iterator, context)

        session = AsyncSessionFactory()
        try:
            response = await method(request_or_iterator, context, session)
            return response
        except Exception as e:
            print("Auth拦截器错误: ", e)
            await context.abort(code=StatusCode.INTERNAL, details=str(e))
        finally:
            await session.close()
