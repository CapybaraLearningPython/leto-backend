import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc

async def main():
    channel = grpc.aio.insecure_channel("127.0.0.1:57917")
    stub = health_pb2_grpc.HealthStub(channel)
    response = await stub.Check(health_pb2.HealthCheckRequest(service=""))
    print(response.status)

import asyncio
asyncio.run(main())