from fastapi import FastAPI
from routers import auth, user, seckill, admin
import uvicorn
import settings
from fastapi.middleware.cors import CORSMiddleware
from hooks.middlewares import ErrorHandlerMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "errors": [
                {
                    "field": e["loc"][-1],
                    "message": e["msg"]
                }
                for e in exc.errors()
            ]
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlerMiddleware)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(seckill.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.GATEWAY_SERVER_PORT)
