from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            print(f"Gateway中间件捕获异常: {e}")
            return JSONResponse(
                content={"detail": f"Gateway中间件捕获异常：{str(e)}"}, 
                status_code=500
            )