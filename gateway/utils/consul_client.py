import consul.aio
from . import single
import settings
from fastapi.exceptions import HTTPException
from fastapi import status


class ConsulClient(metaclass=single.SingletonMeta):
    def __init__(self):
        self.client = None

    def _init_client(self):
        if self.client is None:
            self.client = consul.aio.Consul(
                host=settings.CONSUL_HOST, port=settings.CONSUL_PORT
            )

    async def get_services(self, name):
        self._init_client()
        _, service_objs = await self.client.health.service(name, passing=True)
        services = []
        for service_obj in service_objs:
            service = (
                f"{service_obj['Service']['Address']}:{service_obj['Service']['Port']}"
            )
            services.append(service)
        if not services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consul服务发现失败：没有可用服务！",
            )
        return services


consul_client = ConsulClient()
