from proto import auth_pb2_grpc, user_pb2_grpc, seckill_pb2_grpc
import grpc
import settings
from utils.load_balancer import load_balancer
import httpx
from fastapi import HTTPException


class AuthStub:
    def __init__(self):
        self.channel = None

    async def _init_channel(self):
        if self.channel is None:
            self.channel = grpc.aio.insecure_channel(
                await load_balancer.get_service_address("auth_service")
            )

    async def __aenter__(self):
        await self._init_channel()
        stub = auth_pb2_grpc.AuthServiceStub(self.channel)
        return stub

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class UserStub:
    def __init__(self):
        self.channel = None

    async def _init_channel(self):
        if self.channel is None:
            self.channel = grpc.aio.insecure_channel(
                await load_balancer.get_service_address("user_service")
            )

    async def __aenter__(self):
        await self._init_channel()
        stub = user_pb2_grpc.UserServiceStub(self.channel)
        return stub

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class SeckillStub:
    def __init__(self):
        self.channel = None

    async def _init_channel(self):
        if self.channel is None:
            self.channel = grpc.aio.insecure_channel(
                await load_balancer.get_service_address("seckill_service")
            )

    async def __aenter__(self):
        await self._init_channel()
        stub = seckill_pb2_grpc.SeckillServiceStub(self.channel)
        return stub

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class AdminStub:
    async def __aenter__(self):
        self.base_url = settings.ADMIN_SERVER
        self.client = httpx.AsyncClient(follow_redirects=True)
        return self

    async def make_request(
        self, method: str, path: str, data: dict = None
    ):
        base_url = await load_balancer.get_service_address("admin_service")
        url = f"http://{base_url}/admin/{path}"
        methods = dict(
            get=lambda: self.client.get(url=url),
            post=lambda: self.client.post(url=url, json=data),
            put=lambda: self.client.put(url=url, json=data),
            delete=lambda: self.client.delete(url=url),
            patch=lambda: self.client.patch(url=url, json=data),
        )
        print(">>>>>>>>>>", url)
        response = await methods[method]()
        print(">>>>>> status_code", response.status_code)
        print(">>>>>> content", response.content)
        if response.status_code == 204:
            return {}
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
