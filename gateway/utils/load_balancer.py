from .consul_client import consul_client
import itertools
from typing import List


class LoadBalancer:
    def __init__(self):
        self._iterators = {}

    async def _get_services(self, service_name) -> List:
        services = await consul_client.get_services(service_name)
        return services

    async def get_service_address(self, service_name):
        services = await self._get_services(service_name)
        key = f"{service_name}: {",".join(services)}"

        if key not in self._iterators:
            self._iterators = {
                k: v
                for k, v in self._iterators.items()
                if not k.startswith(f"{service_name}")
            }

            self._iterators[key] = itertools.cycle(services)

        return next(self._iterators[key])
    
load_balancer = LoadBalancer()
