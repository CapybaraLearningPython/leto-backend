import grpc
from proto import seckill_pb2_grpc
from hooks.interceptors import SeckillInterceptor
import asyncio
from services.seckill import SeckillServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer
from utils.consul_client import consul_client


async def main():
    server = grpc.aio.server(interceptors=[SeckillInterceptor()])
    server.add_insecure_port(f"0.0.0.0:{consul_client.port}")

    seckill_pb2_grpc.add_SeckillServiceServicer_to_server(SeckillServicer(), server)

    health_servicer = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

    await server.start()

    await consul_client.register_service()

    print(r"""
   /\_/\  
  (｡•ᴗ•｡)  
  >🍵< """, f' gRPC SeckillService now running...')
    try:
        await server.wait_for_termination()
    finally:
        await consul_client.deregister()

if __name__ == "__main__":
    asyncio.run(main())