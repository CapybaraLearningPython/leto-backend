from grpc_interceptor import AsyncServerInterceptor
import typing
import grpc
from grpc import StatusCode
from models import AsyncSessionFactory
import traceback


class UserInterceptor(AsyncServerInterceptor):
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
        user_id = int(dict(context.invocation_metadata()).get("user-id"))
        if not user_id:
            await context.abort(
                code=StatusCode.UNAUTHENTICATED, details="User拦截器解析user_id失败！"
            )
        try:
            response = await method(request_or_iterator, context, session, user_id)
            return response
        except Exception as e:
            print("User拦截器错误: ", str(e))
            traceback.print_exc() 
            await context.abort(code=StatusCode.INTERNAL, details=str(e))
        finally:
            await session.close()
