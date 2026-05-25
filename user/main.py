import grpc
from proto import user_pb2_grpc
from hooks.interceptors import UserInterceptor
import asyncio
from services.user import UserServicer
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer
from utils.consul_client import consul_client


async def main():
    server = grpc.aio.server(interceptors=[UserInterceptor()])
    server.add_insecure_port(f"0.0.0.0:{consul_client.port}")

    user_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)

    health_servicer = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

    await server.start()

    await consul_client.register_service()

    print(r"""
   /\_/\  
  (｡•ᴗ•｡)  
  >🍵< """, f' gRPC UserService now running...')
    try:
        await server.wait_for_termination()
    finally:
        await consul_client.deregister()

if __name__ == "__main__":
    asyncio.run(main())