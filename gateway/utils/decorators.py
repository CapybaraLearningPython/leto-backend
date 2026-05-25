from functools import wraps
import grpc
from utils.status_code_mapper import get_http_code
from fastapi.exceptions import HTTPException

def grpc_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except grpc.RpcError as e:
            code = get_http_code(e.code())
            print(e.details())
            raise HTTPException(status_code=code, detail=e.details())
    return wrapper