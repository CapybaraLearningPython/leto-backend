import consul.aio
from . import single
import settings
from .network import get_free_address


class ConsulClient(metaclass=single.SingletonMeta):
    def __init__(self):
        self.client = None
        self.address, self.port = get_free_address()
        self.service_id = f"{settings.SERVICE_NAME}-{self.address}-{self.port}"
    
    def _init_client(self):
        if self.client is None:
            self.client = consul.aio.Consul(
                host=settings.CONSUL_HOST, port=settings.CONSUL_PORT
            )

    async def register_service(self):
        self._init_client()
        await self.client.agent.service.register(
            name=settings.SERVICE_NAME,
            service_id=self.service_id,
            address=self.address,
            port=self.port,
            check={
                "GRPC": f"{self.address}:{self.port}",
                "GRPCUseTLS": False,
                "Interval": "10s",
                "Timeout": "5s",
                "DeregisterCriticalServiceAfter": "30s",
            },
        )

    async def deregister(self):
        self._init_client()
        await self.client.agent.service.deregister(self.service_id)


consul_client = ConsulClient()
