import consul
from . import single
from django.conf import settings
from .network import get_free_address


class ConsulClient(metaclass=single.SingletonMeta):
    def __init__(self):
        self.client = consul.Consul(
            host=settings.CONSUL_HOST, port=settings.CONSUL_PORT
        )
        self.address, self.port = get_free_address()
        self.service_id = f"{settings.SERVICE_NAME}-{self.address}-{self.port}"

    def register_service(self):
        self.client.agent.service.register(
            name=settings.SERVICE_NAME,
            service_id=self.service_id,
            address=self.address,
            port=self.port,
            check={
                "HTTP": f"http://{self.address}:{self.port}/admin/health_check/",
                "Interval": "10s",
                "Timeout": "5s",
                "DeregisterCriticalServiceAfter": "30s",
            }
        )

    def deregister(self):
        self.client.agent.service.deregister(self.service_id)

    def deregister_all(self):
        services = self.client.agent.services()
        for service_id in services:
            if service_id.startswith(settings.SERVICE_NAME):
                self.client.agent.service.deregister(service_id)


consul_client = ConsulClient()